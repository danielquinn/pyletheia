import binascii
import hashlib
import json
import os
import re
import urllib.parse

import requests
import six

import magic
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, utils

from ..common import LoggingMixin
from ..exceptions import (
    InvalidURLError,
    PublicKeyNotExistsError,
    UnknownFileTypeError
)


class File(LoggingMixin):
    """
    The base class for any type of file we want to sign.
    """

    SCHEMA_VERSION = 1

    def __init__(self, source, public_key_cache):
        """
        :param source: Typically this will be a file path, but some modules may
               support other types as well.  See ``images.JpegFile`` for an
               example.
        :param public_key_cache: The location on-disk where you're caching
               public keys that have been downloaded for use in verification.
        """

        if isinstance(source, six.string_types):
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

        mimetype = magic.from_file(path, mime=True)
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

    def sign(self, private_key, public_key_url):
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

    def verify(self):
        """
        Attempt to verify the origin of a file by checking its local signature
        against the public key listed in the file.
        :return: boolean  ``True`` if verified, `False`` if not.
        """
        raise NotImplementedError()

    def generate_signature(self, private_key):
        """
        Use the private key to generate a signature from raw image data.

        :param private_key: The private key with which we sign the data.
        :return: str A signature, encoded as base64
        """
        return binascii.hexlify(private_key.sign(
            self.get_raw_data(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        ))

    def generate_payload(self, public_key_url, signature):
        return json.dumps({
            "version": self.SCHEMA_VERSION,
            "public-key": public_key_url,
            "signature": signature.decode()
        }, separators=(",", ":"))

    def verify_signature(self, key_url, signature):
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

    def _get_public_key(self, url):
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


class LargeFile(File):
    """
    For larger files like audio & video, the signature methods are a little
    different so we don't end up busting our RAM limits.
    """

    def generate_signature(self, private_key):

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
