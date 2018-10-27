import os
from hashlib import md5
from unittest import mock

from cryptography.exceptions import InvalidSignature

from aletheia.exceptions import UnparseableFileError
from aletheia.file_types import HtmlFile

from ...base import TestCase


class HtmlTestCase(TestCase):

    def test_get_raw_data(self):
        unsigned = os.path.join(self.DATA, "original", "test.html")
        self.assertEqual(
            md5(HtmlFile(unsigned, "").get_raw_data()).hexdigest(),
            "da4f4a458f2bc6d4b798380e32dcde9d"
        )

        signed = os.path.join(self.DATA, "signed", "test.html")
        self.assertEqual(
            md5(HtmlFile(signed, "").get_raw_data()).hexdigest(),
            "da4f4a458f2bc6d4b798380e32dcde9d",
            "Modifying the metadata should have no effect on the raw data"
        )

    def test_sign(self):

        path = self.copy_for_work("original", "html")

        f = HtmlFile(path, "")
        f.generate_signature = mock.Mock(return_value="signature")
        f.generate_payload = mock.Mock(return_value="payload")
        f.sign(None, "")

        with open(path) as f:
            self.assertIn('<!-- aletheia:', f.read())

    def test_verify_no_signature(self):

        path = self.copy_for_work("original", "html")

        f = HtmlFile(path, "")
        self.assertRaises(UnparseableFileError, f.verify)

    def test_verify_bad_signature(self):

        cache = self.cache_public_key()
        path = self.copy_for_work("bad", "html")

        f = HtmlFile(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify_broken_signature(self):

        cache = self.cache_public_key()
        path = self.copy_for_work("broken", "html")

        f = HtmlFile(path, cache)
        self.assertRaises(UnparseableFileError, f.verify)

    def test_verify(self):

        path = self.copy_for_work("signed", "html")

        f = HtmlFile(path, "")
        f.verify_signature = mock.Mock(return_value=True)
        self.assertTrue(f.verify())
