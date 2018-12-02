import tempfile
import logging
import os
import shutil
from unittest import TestCase as BaseTestCase

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key
)


class TestCase(BaseTestCase):

    DATA = os.path.join(os.path.dirname(__file__), "data")

    # A hash of example.com
    EXAMPLE_DOT_COM = "020506e9b65ec049e227e0a25dfafa84ebfc8eb366b6ce9731d757ae96ee223a14c0a51d6d8a72d45b71b6c779f2dd58841f29180827096a129145c5bcf608e6"  # NOQA: E501

    def __init__(self, *args):
        super(TestCase, self).__init__(*args)
        logging.basicConfig(level=logging.DEBUG)

    def setUp(self):
        self.scratch = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.scratch, "public-keys"), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.scratch, ignore_errors=True)

    def get_private_key(self):
        with open(os.path.join(self.DATA, "keys", "private.pem"), "rb") as f:
            return load_pem_private_key(f.read(), None, default_backend())

    def get_public_key(self):
        with open(os.path.join(self.DATA, "keys", "public.pkcs1"), "rb") as f:
            return load_pem_public_key(f.read(), default_backend())

    def cache_public_key(self) -> str:
        cache = os.path.join(self.scratch, "public-keys")
        shutil.copy(
            os.path.join(self.DATA, "keys", "public.pkcs1"),
            os.path.join(cache, self.EXAMPLE_DOT_COM)
        )
        return cache

    def copy_for_work(self, directory: str, type_: str) -> str:
        """
        Copy our test file to ``scratch`` so we can fiddle with it.
        """
        path = os.path.join(self.scratch, "test.{}".format(type_))
        shutil.copyfile(
            os.path.join(self.DATA, directory, "test.{}".format(type_)),
            path
        )
        return path
