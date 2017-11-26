import base64
import json
import logging
import os

from hashlib import sha512

import requests
import pyexiv2

from PIL import Image
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


class Aletheia:

    SCHEMA_VERSION = 1
    KEY_SIZE = 8192
    PRIVATE_KEY_NAME = "ALETHEIA_PRIVATE_KEY"

    _logger = None

    def __init__(self, private_key_path=None, public_key_path=None, cache_dir=None):  # NOQA: E501

        join = os.path.join

        home = os.getenv(
            "ALETHEIA_HOME", join(os.getenv("HOME"), ".config", "aletheia"))

        self.private_key_path = private_key_path or join(home, "aletheia.pem")
        self.public_key_path = public_key_path or join(home, "aletheia.pub")
        self.public_key_cache = cache_dir or join(home, "public-keys")

        self.logger.debug(
            "init: %s, %s, %s",
            self.private_key_path,
            self.public_key_cache,
            self.public_key_cache
        )

    @property
    def logger(self):

        if self._logger:
            return self._logger

        self._logger = logging.getLogger(
            ".".join([__name__, self.__class__.__name__]))

        return self.logger

    def generate(self):
        """
        Generate a public and private key pair and store them on-disk.
        :return: None
        """

        os.makedirs(
            os.path.dirname(self.private_key_path), exist_ok=True, mode=0o700)

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.KEY_SIZE,
            backend=default_backend()
        )

        open_args = (self.private_key_path, os.O_WRONLY | os.O_CREAT, 0o600)
        with os.fdopen(os.open(*open_args), "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        with open(self.public_key_path, "wb") as f:
            f.write(private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

    def sign(self, path, public_key_url):
        """
        Use Pillow to capture the raw image data, generate a signature from it,
        and then use exiv2 to write said signature + where to find the public
        key to the image metadata in the following format:

          {"version": int, "public-key": url, "signature": signature}

        :param path            str  The path to the file you want to sign
        :param public_key_url  str  The URL where you're storing the public key

        :return None
        """

        if not os.path.exists(path):
            raise FileNotFoundError("Specified file doesn't exist")

        with Image.open(path) as im:
            signature = self._generate_signature(im)

        self.logger.debug("Signature generated: %s", signature)

        payload = json.dumps({
            "version": self.SCHEMA_VERSION,
            "public-key": public_key_url,
            "signature": signature.decode()
        }, separators=(",", ":"))

        metadata = pyexiv2.ImageMetadata(path)
        metadata.read()
        metadata["Xmp.plus.ImageCreatorID"] = payload
        metadata.write()

    def verify(self, path):
        """
        Attempt to verify the origin of an image by checking its local
        signature against the public key listed in the file.

        :param path:  str  The path to the file you want to verify

        :return: boolean  ``True`` if verified, `False`` if not.
        """

        if not os.path.exists(path):
            raise FileNotFoundError("Specified file doesn't exist")

        metadata = pyexiv2.ImageMetadata(path)
        metadata.read()

        try:
            data = json.loads(metadata["Xmp.plus.ImageCreatorID"].value)
            key_url = data["public-key"]
            signature = data["signature"]
        except (KeyError, json.JSONDecodeError):
            self.logger.error("Invalid format, or no signature found")
            return False

        self.logger.debug("Signature found: %s", signature)

        with Image.open(path) as im:
            try:
                self._verify_signature(signature.encode("utf-8"), key_url, im)
                return True
            except InvalidSignature:
                self.logger.error("Bad signature")
                return False

    def _get_private_key(self):
        """
        Try to set the private key by either (a) pulling it from the
        environment, or (b) sourcing it from a file in a known location.
        """

        environment_key = os.getenv(self.PRIVATE_KEY_NAME)
        if environment_key:
            environment_key = bytes(environment_key.encode("utf-8"))
            if b"BEGIN RSA PRIVATE KEY" in environment_key.split(b"\n")[0]:
                return serialization.load_pem_private_key(
                     environment_key,
                     password=None,
                     backend=default_backend()
                )

        if os.path.exists(self.private_key_path):
            with open(self.private_key_path, "rb") as f:
                return serialization.load_pem_private_key(
                     f.read(),
                     password=None,
                     backend=default_backend()
                )

        raise RuntimeError(
            "You don't have a private key defined, so signing is currently "
            "impossible.  Either generate a key and store it at {} or put the "
            "key into an environment variable called {}.".format(
                self.private_key_path,
                self.PRIVATE_KEY_NAME
            )
        )

    def _get_public_key(self, url):
        """
        Attempt to fetch the public key from the local cache, and if it's not
        in there, fetch it from the internetz and put it in there.
        :param url: The URL for the public key's location
        :return: The public key
        """

        os.makedirs(self.public_key_cache, exist_ok=True)

        cache = os.path.join(self.public_key_cache, sha512(url.encode("utf-8")).hexdigest())

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

    def _generate_signature(self, image):
        """
        Use the private key to generate a signature from raw image data.

        :param image: A Pillow ``Image`` object
        :return: str A signature, encoded as base64
        """
        return base64.encodebytes(self._get_private_key().sign(
            image.tobytes(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )).strip()

    def _verify_signature(self, signature, url, image):
        """
        Use the public key (found either by fetching it online or pulling it
        from the local cache to verify the signature against the image data.
        This method raises an exception on failure, returns None on a pass.

        :param signature: The signature found in the file
        :param url: The URL where the public key should be found
        :param image: A Pillow ``Image`` object
        :return: None
        """
        self._get_public_key(url).verify(
            base64.decodebytes(signature),
            image.tobytes(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
