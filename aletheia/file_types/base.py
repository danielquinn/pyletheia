import binascii
import errno
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.parse

import magic
import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, utils
from collections import OrderedDict

from ..common import LoggingMixin
from ..exceptions import (
    DependencyMissingError,
    InvalidURLError,
    PublicKeyNotExistsError,
    UnknownFileTypeError,
    UnparseableFileError
)


class File(LoggingMixin):
    """
    The base class for any type of file we want to sign.
    """

    SCHEMA_VERSION = 1

    def __init__(self, source, public_key_cache: str):
        """
        :param source: Typically this will be a file path, but some modules may
               support other types as well.  See ``images.JpegFile`` for an
               example.
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

        mimetype = cls._guess_mimetype(path)
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

    def sign(self, private_key, public_key_url: str) -> None:
        """
        Override this method to generate a signature from the raw data of your
        particular file format and write it to the metadata layer in the
        following format:

          {"version": int, "public-key": url, "signature": signature}

        :param private_key     key  The private key used for signing
        :param public_key_url  str  The URL where you're storing the public key

        :return None
        """
        raise NotImplementedError()

    def verify(self) -> str:
        """
        Attempt to verify the origin of a file by checking its local signature
        against the public key listed in the file.
        :return: str  The domain from which the file originates.
        """
        raise NotImplementedError()

    def generate_signature(self, private_key) -> bytes:
        """
        Use the private key to generate a signature from raw image data.

        :param private_key: The private key with which we sign the data.
        :return: str  A signature, encoded with hexlify
        """
        return binascii.hexlify(private_key.sign(
            self.get_raw_data(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        ))

    def generate_payload(self, public_key_url: str, signature: bytes):
        """
        Dictionaries are unordered in Python 3.5 and earlier, so to make sure
        the payload is generated in a predictable fashion, we have to use an
        OrderedDict here.
        """

        r = OrderedDict()
        r["version"] = self.SCHEMA_VERSION
        r["public-key"] = public_key_url
        r["signature"] = signature.decode()

        return json.dumps(r, separators=(",", ":"))

    def verify_signature(self, key_url: str, signature: bytes):
        """
        Use the public key (found either by fetching it online or pulling it
        from the local cache to verify the signature against the image data.
        This method returns the domain of the verified server on success, and
        raises an InvalidSignature on failure.

        :param key_url: The URL for the public key we'll use to verify the file
        :param signature: The signature found in the file
        """

        try:
            self._get_public_key(key_url).verify(
                binascii.unhexlify(signature),
                self.get_raw_data(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        except (InvalidSignature, binascii.Error):
            self.logger.error("Bad signature")
            raise InvalidSignature()

        return re.sub(r":.*", "", urllib.parse.urlparse(key_url).netloc)

    def _get_public_key(self, url: str):
        """
        Attempt to fetch the public key from the local cache, and if it's not
        in there, fetch it from the internetz and put it in there.
        :param url: The URL for the public key's location
        :return: The public key
        """

        if not url:
            raise InvalidURLError()

        os.makedirs(self.public_key_cache, exist_ok=True)

        cache = os.path.join(
            self.public_key_cache,
            hashlib.sha512(url.encode("utf-8")).hexdigest()
        )

        if os.path.exists(cache):
            with open(cache, "rb") as f:
                return serialization.load_pem_public_key(
                     f.read(),
                     backend=default_backend()
                )

        response = requests.get(url)
        if response.status_code == 200:
            if b"BEGIN PUBLIC KEY" in response.content:
                with open(cache, "wb") as f:
                    f.write(requests.get(url).content)
                return self._get_public_key(url)

        raise PublicKeyNotExistsError()

    @staticmethod
    def _guess_mimetype(path) -> str:
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
    different so we don't end up busting our RAM limits.
    """

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

    def verify_signature(self, key_url, signature):

        block_size = 16 * 1024

        chosen_hash = hashes.SHA512()
        hasher = hashes.Hash(chosen_hash, default_backend())
        raw = self.get_raw_data()

        buffer = raw.read(block_size)
        while len(buffer) > 0:
            hasher.update(buffer)
            buffer = raw.read(block_size)

        try:
            self._get_public_key(key_url).verify(
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

        return re.sub(r":.*", "", urllib.parse.urlparse(key_url).netloc)


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
            ).stdout.read().decode().strip().split("=")[1].encode()
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

    def sign(self, private_key, public_key_url) -> None:

        signature = self.generate_signature(private_key)

        self.logger.debug("Signature generated: %s", signature)

        payload = self.generate_payload(public_key_url, signature)
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

            key_url = payload["public-key"]
            signature = payload["signature"]

        except (ValueError, TypeError, IndexError, json.JSONDecodeError):
            self.logger.error("Invalid format, or no signature found")
            raise UnparseableFileError()

        return self.verify_signature(key_url, signature)

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
        ).stdout

        needle = "{}=".format(self._get_metadata_key())
        for line in metadata.readlines():
            line = line.decode()
            if line.startswith(needle):
                return json.loads(line.split("=", 1)[-1])

        raise IndexError()  # Will be caught in .verify()
