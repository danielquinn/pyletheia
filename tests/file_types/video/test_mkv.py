import os
import subprocess
from hashlib import md5
from unittest import mock

from cryptography.exceptions import InvalidSignature

from aletheia.exceptions import UnparseableFileError
from aletheia.file_types.video.mkv import MkvFile

from ...base import TestCase


class MkvTestCase(TestCase):

    def test_get_raw_data_from_path(self):

        unsigned = os.path.join(self.DATA, "original", "test.mkv")
        self.assertEqual(
            md5(MkvFile(unsigned, "").get_raw_data()).hexdigest(),
            "4615032ec7809abe6a71cde68bf1be68"
        )

        signed = os.path.join(self.DATA, "signed", "test.mkv")
        self.assertEqual(
            md5(MkvFile(signed, "").get_raw_data()).hexdigest(),
            "4615032ec7809abe6a71cde68bf1be68",
            "Modifying the metadata should have no effect on the raw data"
        )

    def test_sign_from_path(self):

        path = self.copy_for_work("original", "mkv")

        f = MkvFile(path, "")
        f.generate_signature = mock.Mock(return_value="signature")
        f.generate_payload = mock.Mock(return_value="payload")
        f.sign(None, "")

        metadata = subprocess.Popen(
            (
                "ffmpeg",
                "-i", path,
                "-loglevel", "error",
                "-f", "ffmetadata", "-",
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        ).stdout.read()

        self.assertIn(b"ALETHEIA=payload", metadata)

    def test_verify_from_path_no_signature(self):

        path = self.copy_for_work("original", "mkv")

        f = MkvFile(path, "")
        self.assertRaises(UnparseableFileError, f.verify)

    def test_verify_bad_signature(self):
        cache = self.cache_public_key()
        path = self.copy_for_work("bad", "mkv")

        f = MkvFile(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify_broken_signature(self):
        cache = self.cache_public_key()
        path = self.copy_for_work("broken", "mkv")

        f = MkvFile(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify_from_path(self):

        path = self.copy_for_work("signed", "mkv")

        f = MkvFile(path, "")
        f.verify_signature = mock.Mock(return_value=True)
        self.assertTrue(f.verify())
