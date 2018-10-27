import os
import subprocess
from hashlib import md5
from unittest import mock

from cryptography.exceptions import InvalidSignature

from aletheia.exceptions import UnparseableFileError
from aletheia.file_types.video.mp4 import Mp4File

from ...base import TestCase


class Mp4TestCase(TestCase):

    def test_get_raw_data_from_path(self):

        unsigned = os.path.join(self.DATA, "original", "test.mp4")
        self.assertEqual(
            md5(Mp4File(unsigned, "").get_raw_data()).hexdigest(),
            "697bc4588af4bde036171f724175e3e0"
        )

        signed = os.path.join(self.DATA, "signed", "test.mp4")
        self.assertEqual(
            md5(Mp4File(signed, "").get_raw_data()).hexdigest(),
            "697bc4588af4bde036171f724175e3e0",
            "Modifying the metadata should have no effect on the raw data"
        )

    def test_sign_from_path(self):

        path = self.copy_for_work("original", "mp4")

        f = Mp4File(path, "")
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

        self.assertIn(b"comment=payload", metadata)

    def test_verify_from_path_no_signature(self):

        path = self.copy_for_work("original", "mp4")

        f = Mp4File(path, "")
        self.assertRaises(UnparseableFileError, f.verify)

    def test_verify_bad_signature(self):
        cache = self.cache_public_key()
        path = self.copy_for_work("bad", "mp4")

        f = Mp4File(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify_broken_signature(self):
        cache = self.cache_public_key()
        path = self.copy_for_work("broken", "mp4")

        f = Mp4File(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify_from_path(self):

        path = self.copy_for_work("signed", "mp4")

        f = Mp4File(path, "")
        f.verify_signature = mock.Mock(return_value=True)
        self.assertTrue(f.verify())
