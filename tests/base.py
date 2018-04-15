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

    def copy_for_work(self, name):
        """
        Copy our test file to SCRATCH so we can fiddle with it.
        """
        path = os.path.join(self.SCRATCH, name)
        shutil.copyfile(os.path.join(self.DATA, name), path)
        return path
