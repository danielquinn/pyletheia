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
    SCRATCH = os.getenv("ALETHEIA_SCRATCH", "/tmp/aletheia-tests")

    # A hash of https://example.com/aletheia.pub
    EXAMPLE_DOT_COM = "3a6d1800cf22c948c65cec99d968d75dce1611d765c27d87e5b36df7959be1daebbac32b1007cc0f417912e2cc49245c1d01666270c910451cf4cecead9922e7"  # NOQA: E501

    def __init__(self, *args):
        super(TestCase, self).__init__(*args)
        logging.basicConfig(level=logging.DEBUG)

    def setUp(self):
        shutil.rmtree(self.SCRATCH, ignore_errors=True)
        os.makedirs(os.path.join(self.SCRATCH, "public-keys"), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.SCRATCH, ignore_errors=True)

    def get_private_key(self):
        with open(os.path.join(self.DATA, "key.pem"), "rb") as f:
            return load_pem_private_key(f.read(), None, default_backend())

    def get_public_key(self):
        with open(os.path.join(self.DATA, "key.pub"), "rb") as f:
            return load_pem_public_key(f.read(), default_backend())

    def cache_public_key(self) -> str:
        cache = os.path.join(self.SCRATCH, "public-keys")
        shutil.copy(
            os.path.join(self.DATA, "key.pub"),
            os.path.join(cache, self.EXAMPLE_DOT_COM)
        )
        return cache

    def copy_for_work(self, name: str) -> str:
        """
        Copy our test file to SCRATCH so we can fiddle with it.
        """
        path = os.path.join(self.SCRATCH, name)
        shutil.copyfile(os.path.join(self.DATA, name), path)
        return path
