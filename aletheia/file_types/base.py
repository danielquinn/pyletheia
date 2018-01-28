import base64
import hashlib
import os

import magic
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from ..common import LoggingMixin
from ..exceptions import UnknownFileTypeError


class File(LoggingMixin):
    """
    The base class for any type of file we want to sign.
    """

    SUPPORTED_TYPES = ()

    def __init__(self, path, public_key_cache):
        self.path = path
        self.public_key_cache = public_key_cache

    @classmethod
    def build(cls, path, public_key_cache):
        """
        Attempt to find a subclass of File that understands this file and
        return an instance of that class.

        :param path: A path to a file we want to sign/verify.
        :param public_key_cache: The location of the local public key cache.
        :return: An instance of the relevant File subclass
        """

        mimetype = magic.from_file(path, mime=True)
        for klass in cls.__subclasses__():
            if mimetype in klass.SUPPORTED_TYPES:
                return klass(path, public_key_cache)
        raise UnknownFileTypeError()

    def sign(self, private_key, public_key_url):
        raise NotImplementedError()

    def verify(self):
        raise NotImplementedError()

    def _generate_signature(self, private_key, raw_data):
        """
        Use the private key to generate a signature from raw image data.

        :param private_key: The private key with which we sign the data.
        :param raw_data: Binary data we want to sign.
        :return: str A signature, encoded as base64
        """
        return base64.encodebytes(private_key.sign(
            raw_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )).strip()

    def _verify_signature(self, public_key, signature, raw_data):
        """
        Use the public key (found either by fetching it online or pulling it
        from the local cache to verify the signature against the image data.
        This method raises an exception on failure, returns None on a pass.

        :param public_key: The public key we use to verify the file
        :param signature: The signature found in the file
        :param raw_data: Binary data we want to verify
        :return: None
        """
        public_key.verify(
            base64.decodebytes(signature),
            raw_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def _get_public_key(self, url):
        """
        Attempt to fetch the public key from the local cache, and if it's not
        in there, fetch it from the internetz and put it in there.
        :param url: The URL for the public key's location
        :return: The public key
        """

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

        raise RuntimeError("The specified URL does not contain a public key")
