import os
from hashlib import md5
from unittest import mock

from cryptography.exceptions import InvalidSignature

from aletheia.exceptions import UnparseableFileError
from aletheia.file_types import MarkdownFile

from ...base import TestCase


class MarkdownTestCase(TestCase):

    def test_get_raw_data(self):
        unsigned = os.path.join(self.DATA, "original", "test.md")
        self.assertEqual(
            md5(MarkdownFile(unsigned, "").get_raw_data()).hexdigest(),
            "074c1e868f335c87e0b45f85c29ea0ab"
        )

        signed = os.path.join(self.DATA, "signed", "test.md")
        self.assertEqual(
            md5(MarkdownFile(signed, "").get_raw_data()).hexdigest(),
            "074c1e868f335c87e0b45f85c29ea0ab",
            "Modifying the metadata should have no effect on the raw data"
        )

    def test_sign(self):

        path = self.copy_for_work("original", "md")

        f = MarkdownFile(path, "")
        f.generate_signature = mock.Mock(return_value="signature")
        f.generate_payload = mock.Mock(return_value="payload")
        f.sign(None, "")

        with open(path) as f:
            self.assertIn('[//]: # (aletheia:', f.read())

    def test_verify_no_signature(self):

        path = self.copy_for_work("original", "md")

        f = MarkdownFile(path, "")
        self.assertRaises(UnparseableFileError, f.verify)

    def test_verify_bad_signature(self):

        cache = self.cache_public_key()
        path = self.copy_for_work("bad", "md")

        f = MarkdownFile(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify_broken_signature(self):

        cache = self.cache_public_key()
        path = self.copy_for_work("broken", "md")

        f = MarkdownFile(path, cache)
        self.assertRaises(UnparseableFileError, f.verify)

    def test_verify_future_version(self):
        path = self.copy_for_work("future", "md")
        self.assertRaises(UnparseableFileError, MarkdownFile(path, "").verify)

    def test_verify(self):

        path = self.copy_for_work("signed", "md")

        f = MarkdownFile(path, "")
        f.verify_signature = mock.Mock(return_value=True)
        self.assertTrue(f.verify())
