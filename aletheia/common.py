import logging

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from .exceptions import UnrecognisedKey


class LoggingMixin:
    """
    Handy logging mixin that allows me to use a logger without having to
    declare it globally.
    """

    _logger = None

    @property
    def logger(self):

        if self._logger:
            return self._logger

        self._logger = logging.getLogger(
            ".".join(["aletheia", __name__, self.__class__.__name__]))

        return self.logger


def get_key(data: bytes) -> RSAPublicKey:
    """
    Given an arbitrary string in a variety of formats, return a key object.
    """

    kwargs = {"backend": default_backend()}
    data = data.strip()

    if data.startswith(b"-----BEGIN RSA PRIVATE KEY-----"):
        kwargs["password"] = None
        return serialization.load_pem_private_key(data, **kwargs)

    if data.startswith(b"-----BEGIN RSA PUBLIC KEY-----"):
        return serialization.load_pem_public_key(data, **kwargs)

    if data.startswith(b"ssh-rsa "):
        return serialization.load_ssh_public_key(data, **kwargs)

    raise UnrecognisedKey()
