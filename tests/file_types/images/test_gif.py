import os
import subprocess
from hashlib import md5
from unittest import mock

from aletheia.exceptions import UnparseableFileError
from aletheia.file_types import GifFile
from cryptography.exceptions import InvalidSignature

from ...base import TestCase


class GifTestCase(TestCase):

    def test_get_raw_data(self):
        unsigned = os.path.join(self.DATA, "original", "test.gif")
        self.assertEqual(
            md5(GifFile(unsigned, "").get_raw_data()).hexdigest(),
            "aa41bc501a8c9f8532914524c0b046b6"
        )

        signed = os.path.join(self.DATA, "signed", "test.gif")
        self.assertEqual(
            md5(GifFile(signed, "").get_raw_data()).hexdigest(),
            "aa41bc501a8c9f8532914524c0b046b6",
            "Modifying the metadata should have no effect on the raw data"
        )

    def test_sign(self):

        path = self.copy_for_work("original", "gif")

        f = GifFile(path, "")
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

        path = self.copy_for_work("original", "gif")

        f = GifFile(path, "")
        self.assertRaises(UnparseableFileError, f.verify)

    def test_verify_bad_signature(self):

        cache = self.cache_public_key()
        path = self.copy_for_work("bad", "gif")

        f = GifFile(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify_broken_signature(self):

        cache = self.cache_public_key()
        path = self.copy_for_work("broken", "gif")

        f = GifFile(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify_future_version(self):
        path = self.copy_for_work("future", "gif")
        self.assertRaises(UnparseableFileError, GifFile(path, "").verify)

    def test_verify(self):

        path = self.copy_for_work("signed", "gif")

        f = GifFile(path, "")
        f.verify_signature = mock.Mock(return_value=True)
        self.assertTrue(f.verify())
