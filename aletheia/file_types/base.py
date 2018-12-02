import binascii
import errno
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from collections import OrderedDict
from typing import Union

import dns.exception
import dns.resolver
import magic
import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, utils
from cryptography.hazmat.primitives.asymmetric.rsa import (
    RSAPrivateKey,
    RSAPublicKey
)

from ..common import LoggingMixin, get_key
from ..exceptions import (
    DependencyMissingError,
    PublicKeyNotExistsError,
    UnacceptableLocationError,
    UnknownFileTypeError,
    UnparseableFileError,
    UnrecognisedKey
)


class File(LoggingMixin):
    """
    The base class for any type of file we want to sign.
    """

    SCHEMA_VERSION = 2
    CACHE_TIME = 60 * 60  # 1 hour

    # Thanks StackOverflow! https://stackoverflow.com/a/26987741/231670
    DOMAIN_REGEX = re.compile(
        r"^(((?!-))(xn--|_{1,1})?[a-z0-9-]{0,61}[a-z0-9]{1,1}\.)*"
        r"(xn--)?([a-z0-9\-]{1,61}|[a-z0-9-]{1,30}\.[a-z]{2,})$"
    )

    def __init__(self, source: str, public_key_cache: str):
        """
        :param source: A file path
        :param public_key_cache: The location on-disk where you're caching
               public keys that have been downloaded for use in verification.
        """

        if isinstance(source, str):
            if not os.path.exists(source):
                raise FileNotFoundError(
                    "Can't find the file you want to sign/verify: {}".format(
                        source
                    )
                )

        self.source = source
        self.public_key_cache = public_key_cache

    @classmethod
    def build(cls, path: str, public_key_cache: str):
        """
        Attempt to find a subclass of File that understands this file and
        return an instance of that class.

        :param path: A path to a file we want to sign/verify.
        :param public_key_cache: The location of the local public key cache.
        :return: An instance of the relevant File subclass
        """

        mimetype = cls.__guess_mimetype(path)
        for klass in cls.get_subclasses():
            if mimetype in klass.SUPPORTED_TYPES:
                return klass(path, public_key_cache)
        raise UnknownFileTypeError()

    @classmethod
    def get_subclasses(cls):
        for subclass in cls.__subclasses__():
            yield from subclass.get_subclasses()
            if hasattr(subclass, "SUPPORTED_TYPES"):
                yield subclass

    def get_raw_data(self):
        """
        This should return the raw binary data of file -- the part that
        contains the media, so no header data.  This is accomplished in a
        variety of ways, depending on the file format.
        """
        raise NotImplementedError()

    def sign(self, private_key, domain: str) -> None:
        """
        Override this method to generate a signature from the raw data of your
        particular file format and write it to the metadata layer in the
        following format:

          {"version": int, "domain": domain, "signature": signature}

        Typically this involves a call to ``File.generate_payload()`` which
        does all of the heavy-lifting for you.
        """
        raise NotImplementedError()

    def verify(self) -> str:
        """
        Attempt to verify the origin of a file by checking its local signature
        against the public key listed in the file.
        """
        raise NotImplementedError()

    def generate_signature(self, private_key: RSAPrivateKey) -> bytes:
        """
        Use the private key to generate a signature from raw image data.
        """
        return binascii.hexlify(private_key.sign(
            self.get_raw_data(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA512()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA512()
        ))

    def generate_payload(self, domain: str, signature: bytes):
        """
        Dictionaries are unordered in Python 3.5 and earlier, so to make sure
        the payload is generated in a predictable fashion, we have to use an
        OrderedDict here.
        """

        r = OrderedDict()
        r["version"] = self.SCHEMA_VERSION
        r["domain"] = domain
        r["signature"] = signature.decode()

        return json.dumps(r, separators=(",", ":"))

    def check_schema_version(self, version):

        if version > self.SCHEMA_VERSION:
            raise UnparseableFileError(
                "This file was signed by a more modern version of Aletheia. "
                "You'll need to upgrade to verify it."
            )

    def verify_signature(self, domain: str, signature: bytes):
        """
        Use the public key (found either by fetching it online or pulling it
        from the local cache to verify the signature against the image data.
        This method returns the domain of the verified server on success, and
        raises an InvalidSignature on failure.
        """

        if not self.DOMAIN_REGEX.match(domain):
            raise UnacceptableLocationError(
                'The domain name provided, "{}" does not appear to be '
                'valid.'.format(domain)
            )

        try:
            self._get_public_key(domain).verify(
                binascii.unhexlify(signature),
                self.get_raw_data(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA512()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA512()
            )
        except (InvalidSignature, binascii.Error):
            self.logger.error("Bad signature")
            raise InvalidSignature()

        return domain

    def _get_public_key(self,
                        domain: str, use_cache: bool = True) -> RSAPublicKey:
        """
        Attempt to fetch the public key from the local cache, and if it's not
        in there, fetch it from the internetz and put it in there.
        """

        os.makedirs(self.public_key_cache, exist_ok=True)

        cache = os.path.join(
            self.public_key_cache,
            hashlib.sha512(domain.encode("utf-8")).hexdigest()
        )

        if use_cache:

            if os.path.exists(cache):

                # Cache invalidation based on modified time
                now = time.time()
                then = os.path.getmtime(cache)
                if now - then > self.CACHE_TIME:
                    os.unlink(cache)
                else:
                    with open(cache, "rb") as f:
                        return get_key(f.read())

        key = None

        try:
            key = self.__get_public_key_from_dns(domain)
        except (PublicKeyNotExistsError, UnrecognisedKey):
            try:
                key = self.__get_public_key_from_url(domain)
            except (PublicKeyNotExistsError, UnrecognisedKey):
                pass  # We fall through below with no key

        if key is None:
            raise PublicKeyNotExistsError(
                "The public key could not be found at {}".format(domain)
            )

        with open(cache, "w") as f:
            f.write(key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.PKCS1
            ).decode().strip())

        return key

    def __get_public_key_from_dns(self,
                                  domain: str) -> Union[RSAPublicKey, None]:

        try:

            response = dns.resolver.query(domain, "TXT").response
            for answer in response.answer:
                for rdata in answer:
                    txt = b"".join(rdata.strings)
                    if txt.startswith(b"aletheia-public-key="):
                        return get_key(txt[20:])

        except dns.exception.DNSException as e:

            # A DNS/network error broke things
            self.logger.warning(
                "The public key could not be found at {} due to the following "
                "error: {}".format(domain, e)
            )

    def __get_public_key_from_url(self,
                                  domain: str) -> Union[RSAPublicKey, None]:

        url = "https://{}/aletheia.pub".format(domain)
        try:
            print(1)
            response = requests.get(url)
            print(2)
        except requests.exceptions.RequestException:
            self.logger.warning(
                "Can't connect to {} to acquire the public key".format(url))
            return

        if response.status_code == 200:
            return get_key(response.content)

    @staticmethod
    def __guess_mimetype(path: str) -> str:
        """
        We use the file-magic module to get this value, but if that returns a
        type that doesn't mean anything to us, we fall back to guessing based
        on the file suffix.
        """

        ambiguous_mimetypes = (
            "text/plain",
            "application/octet-stream"
        )

        guessed = magic.detect_from_filename(path).mime_type
        if guessed not in ambiguous_mimetypes:
            return guessed

        return {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
            "png": "image/png",
            "mp3": "audio/mp3",
            "mp4": "video/mp4",
            "htm": "text/html",
            "html": "text/html",
            "md": "text/markdown",
            "mkv": "video/x-matroska",
            "ogv": "video/ogg",
            "webm": "video/webm",
        }.get(path.split(".")[-1].lower(), guessed)


class LargeFile(File):
    """
    For larger files like audio & video, the signature methods are a little
    different so we don't end up busting our RAM limits.  This isn't used at
    the moment, but as we expand the number of supported formats, it may come
    in handy.
    """

    def get_raw_data(self):
        return super().get_raw_data()

    def sign(self, private_key, domain: str):
        return super().sign(private_key, domain)

    def verify(self):
        return super().verify()

    def generate_signature(self, private_key) -> bytes:

        block_size = 16 * 1024
        raw_data = self.get_raw_data()

        chosen_hash = hashes.SHA512()
        hasher = hashes.Hash(chosen_hash, default_backend())

        buffer = raw_data.read(block_size)
        while len(buffer) > 0:
            hasher.update(buffer)
            buffer = raw_data.read(block_size)

        return binascii.hexlify(private_key.sign(
            hasher.finalize(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA512()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            utils.Prehashed(chosen_hash)
        ))

    def verify_signature(self, domain: str, signature: str):

        block_size = 16 * 1024

        chosen_hash = hashes.SHA512()
        hasher = hashes.Hash(chosen_hash, default_backend())
        raw = self.get_raw_data()

        buffer = raw.read(block_size)
        while len(buffer) > 0:
            hasher.update(buffer)
            buffer = raw.read(block_size)

        try:
            self._get_public_key(domain).verify(
                binascii.unhexlify(signature),
                hasher.finalize(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA512()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                utils.Prehashed(chosen_hash)
            )
        except (InvalidSignature, binascii.Error):
            self.logger.error("Bad signature")
            raise InvalidSignature()

        return domain


class FFmpegFile(File):
    """
    Large files that use FFmpeg to derive the raw data can subclass this since
    the tactic is the same across formats.
    """

    def get_raw_data(self) -> bytes:
        """
        Strictly speaking, this isn't the "raw data" but rather a hash of it,
        this is due to the fact that ffmpeg is crazy-powerful and can do
        hashing of Very Large Files internally.  It also doesn't make accessing
        the raw data particularly easy from version to version, so this is the
        best I think we can get.
        """

        try:
            return subprocess.Popen(
                (
                    "ffmpeg",
                    "-loglevel", "error",
                    "-i", self.source,
                    "-f", "hash",
                    "-hash", "sha512", "-"
                ),
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            ).communicate()[0].decode().strip().split("=")[1].encode()
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise DependencyMissingError(
                    "Handling this file type requires a working installation "
                    "of FFmpeg (https://ffmpeg.org/) and for the moment, "
                    "Aletheia can't find one on this system.  If you're sure "
                    "it's installed, make sure that it's callable from the "
                    "PATH, and if it isn't installed, you can follow the "
                    "instructions on the FFmpeg website for how to do that.  "
                    "Don't worry, it's pretty easy."
                )
            raise

    def sign(self, private_key, domain: str) -> None:

        signature = self.generate_signature(private_key)

        self.logger.debug("Signature generated: %s", signature)

        payload = self.generate_payload(domain, signature)
        scratch = os.path.join(
            tempfile.mkdtemp(prefix="aletheia-"),
            "scratch.{}".format(self._get_suffix())
        )

        subprocess.call((
            "ffmpeg",
            "-i", self.source,
            "-loglevel", "error",
            "-metadata", "{}={}".format(self._get_metadata_key(), payload),
            "-codec", "copy", scratch
        ))
        shutil.move(scratch, self.source)
        shutil.rmtree(os.path.dirname(scratch))

    def verify(self) -> str:

        try:

            payload = self._get_payload()

            self.logger.debug("Found payload: %s", payload)

            version = payload["version"]
            domain = payload["domain"]
            signature = payload["signature"]

        except (
                ValueError,
                TypeError,
                IndexError,
                KeyError,
                json.JSONDecodeError
        ):
            raise UnparseableFileError("Invalid format, or no signature found")

        self.check_schema_version(version)

        return self.verify_signature(domain, signature)

    def _get_suffix(self) -> str:
        raise NotImplementedError

    def _get_metadata_key(self) -> str:
        """
        Override this if the format in question has specific rules about the
        keys used in metadata.  See multimedia.cx for more information:
          https://wiki.multimedia.cx/index.php/FFmpeg_Metadata
        """
        return "ALETHEIA"

    def _get_payload(self) -> dict:

        metadata = subprocess.Popen(
            (
                "ffmpeg",
                "-i", self.source,
                "-loglevel", "error",
                "-f", "ffmetadata", "-",
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        ).communicate()[0]

        needle = "{}=".format(self._get_metadata_key())
        for line in metadata.split():
            line = line.decode()
            if line.startswith(needle):
                return json.loads(line.split("=", 1)[-1])

        raise IndexError()  # Will be caught in .verify()
