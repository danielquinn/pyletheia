import os
import subprocess
from hashlib import md5
from unittest import mock

from aletheia.exceptions import UnparseableFileError
from aletheia.file_types import JpegFile
from cryptography.exceptions import InvalidSignature

from ...base import TestCase


class PngTestCase(TestCase):

    def test_get_raw_data(self):
        unsigned = os.path.join(self.DATA, "original", "test.png")
        self.assertEqual(
            md5(JpegFile(unsigned, "").get_raw_data()).hexdigest(),
            "65027be33b8b7b26a95695b5dc582c32"
        )

        signed = os.path.join(self.DATA, "signed", "test.png")
        self.assertEqual(
            md5(JpegFile(signed, "").get_raw_data()).hexdigest(),
            "65027be33b8b7b26a95695b5dc582c32",
            "Modifying the metadata should have no effect on the raw data"
        )

    def test_sign(self):

        path = self.copy_for_work("original", "png")

        f = JpegFile(path, "")
        f.generate_signature = mock.Mock(return_value="signature")
        f.generate_payload = mock.Mock(return_value="payload")
        f.sign(None, "")

        self.assertIn(
            "payload",
            subprocess.Popen(
                ("exiftool", path),
                stdout=subprocess.PIPE
            ).stdout.read().decode()
        )

    def test_verify_no_signature(self):

        path = self.copy_for_work("original", "png")

        f = JpegFile(path, "")
        self.assertRaises(UnparseableFileError, f.verify)

    def test_verify_bad_signature(self):

        cache = self.cache_public_key()
        path = self.copy_for_work("bad", "png")

        f = JpegFile(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify_broken_signature(self):

        cache = self.cache_public_key()
        path = self.copy_for_work("broken", "png")

        f = JpegFile(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify(self):

        path = self.copy_for_work("signed", "png")

        f = JpegFile(path, "")
        f.verify_signature = mock.Mock(return_value=True)
        self.assertTrue(f.verify())
