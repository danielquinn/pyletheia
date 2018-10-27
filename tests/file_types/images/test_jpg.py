import os
import subprocess
from hashlib import md5
from unittest import mock

from aletheia.exceptions import UnparseableFileError
from aletheia.file_types import JpegFile
from cryptography.exceptions import InvalidSignature

from ...base import TestCase


class JpegTestCase(TestCase):

    def test_get_raw_data(self):
        unsigned = os.path.join(self.DATA, "original", "test.jpg")
        self.assertEqual(
            md5(JpegFile(unsigned, "").get_raw_data()).hexdigest(),
            "c08b00b988d086cf0394929f8016b12b"
        )

        signed = os.path.join(self.DATA, "signed", "test.jpg")
        self.assertEqual(
            md5(JpegFile(signed, "").get_raw_data()).hexdigest(),
            "c08b00b988d086cf0394929f8016b12b",
            "Modifying the metadata should have no effect on the raw data"
        )

    def test_sign(self):

        path = self.copy_for_work("original", "jpg")

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

        path = self.copy_for_work("original", "jpg")

        f = JpegFile(path, "")
        self.assertRaises(UnparseableFileError, f.verify)

    def test_verify_bad_signature(self):

        cache = self.cache_public_key()
        path = self.copy_for_work("bad", "jpg")

        f = JpegFile(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify_broken_signature(self):

        cache = self.cache_public_key()
        path = self.copy_for_work("broken", "jpg")

        f = JpegFile(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify(self):

        path = self.copy_for_work("signed", "jpg")

        f = JpegFile(path, "")
        f.verify_signature = mock.Mock(return_value=True)
        self.assertTrue(f.verify())
