import os
from hashlib import md5
from unittest import mock

from cryptography.exceptions import InvalidSignature
import mutagen

from aletheia.exceptions import UnparseableFileError
from aletheia.file_types import Mp4File

from ...base import TestCase


class Mp4TestCase(TestCase):

    def test_get_raw_data_from_path(self):
        unsigned = os.path.join(self.DATA, "test.mp4")
        self.assertEqual(
            md5(Mp4File(unsigned, "").get_raw_data().read()).hexdigest(),
            "b9b28e4ac500be961bd07290a34cf93f"
        )

    def test_sign_from_path(self):

        path = self.copy_for_work("test.mp4")

        f = Mp4File(path, "")
        f.generate_signature = mock.Mock(return_value="signature")
        f.generate_payload = mock.Mock(return_value="payload")
        f.sign(None, None)

        mp4 = mutagen.File(path)
        self.assertEqual(mp4["\xa9too"], ["payload"])

    def test_verify_from_path_no_signature(self):

        path = self.copy_for_work("test.mp4")

        f = Mp4File(path, "")
        self.assertRaises(UnparseableFileError, f.verify)

    def test_verify_bad_signature(self):
        cache = self.cache_public_key()
        path = self.copy_for_work("test-bad-signature.mp4")

        f = Mp4File(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify_broken_signature(self):
        cache = self.cache_public_key()
        path = self.copy_for_work("test-broken-signature.mp4")

        f = Mp4File(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify_from_path(self):

        path = self.copy_for_work("test-signed.mp4")

        f = Mp4File(path, "")
        f.verify_signature = mock.Mock(return_value=True)
        self.assertTrue(f.verify())
