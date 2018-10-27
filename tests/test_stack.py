import os
import shutil
from hashlib import sha512
from unittest.mock import patch

from aletheia.aletheia import Aletheia

from .base import TestCase


class StackTestCase(TestCase):
    """
    Test the entire stack: key generation, and the signing/verifying of every
    file type.
    """

    TEST_TYPES = (
        "mp3",
        "html", 
        "gif", "jpg", "png", 
        "mkv", "mp4", "webm"
    )

    def test_stack(self):

        env = {"HOME": self.scratch, "ALETHEIA_HOME": self.scratch}

        with patch.dict(os.environ, env):

            aletheia = Aletheia()

            self.assertEqual(
                aletheia.public_key_path,
                os.path.join(self.scratch, "aletheia.pub")
            )
            self.assertEqual(
                aletheia.private_key_path,
                os.path.join(self.scratch, "aletheia.pem")
            )
            self.assertEqual(
                aletheia.public_key_cache,
                os.path.join(self.scratch, "public-keys")
            )

            # Generate the keys

            self.assertFalse(
                os.path.exists(os.path.join(self.scratch, "aletheia.pem")))
            self.assertFalse(
                os.path.exists(os.path.join(self.scratch, "aletheia.pub")))

            aletheia.generate()

            self.assertTrue(
                os.path.exists(os.path.join(self.scratch, "aletheia.pem")))
            self.assertTrue(
                os.path.exists(os.path.join(self.scratch, "aletheia.pub")))

            for suffix in self.TEST_TYPES:

                filename = "test.{}".format(suffix)
                source_path = os.path.normpath(os.path.join(
                    os.path.dirname(__file__),
                    "data",
                    "original",
                    filename
                ))

                # Copy our test file to SCRATCH so we can fiddle with it

                file_path = os.path.join(self.scratch, filename)
                shutil.copyfile(source_path, file_path)

                # Sign the file

                public_key_url = "https://example.com/aletheia.pub"
                aletheia.sign(file_path, public_key_url)
                with open(source_path, "rb") as original:
                    with open(file_path, "rb") as modified:
                        self.assertNotEqual(
                            sha512(original.read()),
                            sha512(modified.read())
                        )

                # Put the public key in the cache so we don't try to fetch it.

                shutil.copyfile(
                    os.path.join(self.scratch, "aletheia.pub"),
                    os.path.join(
                        self.scratch,
                        "public-keys",
                        sha512(public_key_url.encode("utf-8")).hexdigest()
                    )
                )

                # Verify the file

                self.assertTrue(aletheia.verify(file_path))
