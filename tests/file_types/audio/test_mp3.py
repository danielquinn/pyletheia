import os
from hashlib import md5
from unittest import mock

from cryptography.exceptions import InvalidSignature
from mutagen.id3 import ID3

from aletheia.exceptions import UnparseableFileError
from aletheia.file_types import Mp3File

from ...base import TestCase


class Mp3TestCase(TestCase):

    def test_get_raw_data_from_path(self):
        unsigned = os.path.join(self.DATA, "test.mp3")
        self.assertEqual(
            md5(Mp3File(unsigned, "").get_raw_data().read()).hexdigest(),
            "8311d858697187b9cac8536221b5591d"
        )

    def test_sign_from_path(self):

        path = self.copy_for_work("test.mp3")

        f = Mp3File(path, "")
        f.generate_signature = mock.Mock(return_value="signature")
        f.generate_payload = mock.Mock(return_value="payload")
        f.sign(None, None)

        audio = ID3(path)
        self.assertEqual(audio["TPUB"], ["payload"])

    def test_verify_from_path_no_signature(self):

        path = self.copy_for_work("test.mp3")

        f = Mp3File(path, "")
        self.assertRaises(UnparseableFileError, f.verify)

    def test_verify_bad_signature(self):
        cache = self.cache_public_key()
        path = self.copy_for_work("test-bad-signature.mp3")

        f = Mp3File(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify_broken_signature(self):
        cache = self.cache_public_key()
        path = self.copy_for_work("test-broken-signature.mp3")

        f = Mp3File(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify_from_path(self):

        path = self.copy_for_work("test-signed.mp3")

        f = Mp3File(path, "")
        f.verify_signature = mock.Mock(return_value=True)
        self.assertTrue(f.verify())
