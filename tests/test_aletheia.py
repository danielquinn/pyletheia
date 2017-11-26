import os
import logging
import shutil

from hashlib import sha512
from unittest.mock import patch
from unittest import TestCase

from aletheia.aletheia import Aletheia


class AletheiaTestCase(TestCase):

    SCRATCH = "/tmp/aletheia-tests"
    IMAGE = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "data", "syntax.jpg"))

    def __init__(self, *args):
        TestCase.__init__(self, *args)
        logging.basicConfig(level=logging.DEBUG)

    def setUp(self):
        os.makedirs(os.path.join(self.SCRATCH, "public-keys"), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.SCRATCH)

    @patch.dict("os.environ", {"ALETHEIA_HOME": SCRATCH})
    def test_stack(self):

        aletheia = Aletheia()

        self.assertEqual(
            aletheia.public_key_path,
            os.path.join(self.SCRATCH, "aletheia.pub")
        )
        self.assertEqual(
            aletheia.private_key_path,
            os.path.join(self.SCRATCH, "aletheia.pem")
        )
        self.assertEqual(
            aletheia.public_key_cache,
            os.path.join(self.SCRATCH, "public-keys")
        )

        # Generate the keys

        self.assertFalse(
            os.path.exists(os.path.join(self.SCRATCH, "aletheia.pem")))
        self.assertFalse(
            os.path.exists(os.path.join(self.SCRATCH, "aletheia.pub")))

        aletheia.generate()

        self.assertTrue(
            os.path.exists(os.path.join(self.SCRATCH, "aletheia.pem")))
        self.assertTrue(
            os.path.exists(os.path.join(self.SCRATCH, "aletheia.pub")))

        # Copy our test file to SCRATCH so we can fiddle with it

        image_path = os.path.join(self.SCRATCH, "syntax.jpg")
        shutil.copyfile(self.IMAGE, image_path)

        # Sign the image

        public_key_url = "https://example.com/aletheia.pub"
        aletheia.sign(image_path, public_key_url)
        with open(self.IMAGE, "rb") as original:
            with open(image_path, "rb") as modified:
                self.assertNotEqual(
                    sha512(original.read()),
                    sha512(modified.read())
                )

        # Put the public key in the cache so we don't try to fetch it.

        shutil.copyfile(
            os.path.join(self.SCRATCH, "aletheia.pub"),
            os.path.join(
                self.SCRATCH,
                "public-keys",
                sha512(public_key_url.encode("utf-8")).hexdigest()
            )
        )

        # Verify the image

        self.assertTrue(aletheia.verify(image_path))
