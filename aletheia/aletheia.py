import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from .common import LoggingMixin, get_key
from .file_types import File


class Aletheia(LoggingMixin):

    KEY_SIZE = 8192
    PRIVATE_KEY_NAME = "ALETHEIA_PRIVATE_KEY"

    def __init__(
            self,
            private_key_path: str = None,
            public_key_path: str = None,
            cache_dir: str = None):

        join = os.path.join

        home = os.getenv(
            "ALETHEIA_HOME", join(os.getenv("HOME"), ".config", "aletheia"))

        self.private_key_path = private_key_path or join(home, "aletheia.pem")
        self.public_key_path = public_key_path or join(home, "aletheia.pub")
        self.public_key_cache = cache_dir or join(home, "public-keys")

        self.logger.debug(
            "init: %s, %s, %s",
            self.private_key_path,
            self.public_key_path,
            self.public_key_cache
        )

    def generate(self) -> None:
        """
        Generate a public and private key pair and store them on-disk.
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
                format=serialization.PublicFormat.PKCS1
            ))

    def sign(self, path: str, domain: str):

        if not os.path.exists(path):
            raise FileNotFoundError(
                "Specified file \"{}\" doesn't exist".format(path)
            )

        File.build(path, self.public_key_cache).sign(
            self._get_private_key(),
            domain
        )

    def verify(self, path: str):

        if not os.path.exists(path):
            raise FileNotFoundError(
                "Specified file \"{}\" doesn't exist".format(path)
            )

        return File.build(path, self.public_key_cache).verify()

    def _get_private_key(self):
        """
        Try to set the private key by either (a) pulling it from the
        environment, or (b) sourcing it from a file in a known location.
        """

        environment_key = os.getenv(self.PRIVATE_KEY_NAME)
        if environment_key:
            environment_key = bytes(environment_key.encode("utf-8"))
            if b"BEGIN RSA PRIVATE KEY" in environment_key.split(b"\n")[0]:
                return get_key(environment_key)

        if os.path.exists(self.private_key_path):
            with open(self.private_key_path, "rb") as f:
                return get_key(f.read())

        raise RuntimeError(
            "You don't have a private key defined, so signing is currently "
            "impossible.  Either generate a key and store it at {} or put the "
            "key into an environment variable called {}.".format(
                self.private_key_path,
                self.PRIVATE_KEY_NAME
            )
        )
