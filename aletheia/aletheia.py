#
# Python API:
#
#   from aletheia import generate, sign, verify
#
#   generate()
#
#   sign(path, public_key_url)
#   sign_bulk(paths, public_key_url)
#
#   verify(path)
#   verify_bulk(paths)
#

import base64
import os
import subprocess
from hashlib import sha512

import requests

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


class Aletheia:

    KEY_SIZE = 8192
    HOME = os.path.join(os.getenv("HOME"), ".aletheia")
    PRIVATE_KEY_PATH = os.path.join(HOME, "aletheia.pem")
    PRIVATE_KEY_NAME = "ALETHEIA_PRIVATE_KEY"
    PUBLIC_KEY_CACHE = os.path.join(HOME, "public-keys")

    @classmethod
    def generate(cls):

        path = cls.HOME
        os.makedirs(cls.HOME, exist_ok=True)

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=cls.KEY_SIZE,
            backend=default_backend()
        )

        private = os.path.join(path, "aletheia.pem")
        perms = os.O_WRONLY | os.O_CREAT
        with os.fdopen(os.open(private, perms, 0o600), "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        with open(os.path.join(path, "aletheia.pub"), "wb") as f:
            f.write(private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

    def sign(self, path, public_key_url):

        if not os.path.exists(path):
            raise FileNotFoundError("Specified file doesn't exist")

        with open(path, "rb") as f:
            image_data = subprocess.check_output(
                ("exiftool", "-all=", "-"),
                stdin=f
            )

        signature = base64.encodebytes(self._get_private_key().sign(
            image_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )).strip()

        subprocess.call((
            "exiftool",
            "-ImageSupplierImageID={}".format(signature.decode("utf-8")),
            "-overwrite_original",
            path
        ))
        subprocess.call((
            "exiftool",
            "-ImageSupplierID={}".format(public_key_url),
            "-overwrite_original",
            path
        ))

    def verify(self, path):

        if not os.path.exists(path):
            raise FileNotFoundError("Specified file doesn't exist")

        with open(path, "rb") as f:

            key_url = subprocess.check_output(
                ("exiftool", "-s", "-s", "-s", "-ImageSupplierID", "-"),
                stdin=f
            ).strip()

            f.seek(0)

            signature = base64.decodebytes(subprocess.check_output(
                ("exiftool", "-s", "-s", "-s", "-ImageSupplierImageID", "-"),
                stdin=f
            ).strip())

            f.seek(0)

            image_data = subprocess.check_output(
                ("exiftool", "-all=", "-"),
                stdin=f
            )

        try:
            self._get_public_key(key_url).verify(
                signature,
                image_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False

    def _get_private_key(self):
        """
        Try to set the private key by either (a) pulling it from the
        environment, or (b) sourcing it from a file in a known location.
        """

        environment_key = os.getenv("ALETHEIA_PRIVATE_KEY")
        if environment_key:
            environment_key = bytes(environment_key.encode("utf-8"))
            if b"BEGIN RSA PRIVATE KEY" in environment_key.split(b"\n")[0]:
                return serialization.load_pem_private_key(
                     environment_key,
                     password=None,
                     backend=default_backend()
                )

        if os.path.exists(self.PRIVATE_KEY_PATH):
            with open(self.PRIVATE_KEY_PATH, "rb") as f:
                return serialization.load_pem_private_key(
                     f.read(),
                     password=None,
                     backend=default_backend()
                )

        raise RuntimeError(
            "You don't have a private key defined, so signing is currently "
            "impossible.  Either generate a key and store it at {} or put the "
            "key into an environment variable called {}.".format(
                self.PRIVATE_KEY_PATH,
                self.PRIVATE_KEY_NAME
            )
        )

    def _get_public_key(self, url):

        os.makedirs(self.PUBLIC_KEY_CACHE, exist_ok=True)

        cache = os.path.join(self.PUBLIC_KEY_CACHE, sha512(url).hexdigest())
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
