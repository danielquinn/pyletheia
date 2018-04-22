import os
from hashlib import md5
from unittest import mock

import piexif

from aletheia.file_types import JpegFile

from ..base import TestCase


class JpegTestCase(TestCase):

    def test_get_raw_data(self):
        unsigned = os.path.join(self.DATA, "test.jpg")
        self.assertEqual(
            md5(JpegFile(unsigned, "").get_raw_data()).hexdigest(),
            "cc96a1bff6c259f0534f191e83cfdf0e"
        )

    def test_sign(self):

        path = self.copy_for_work("test.jpg")

        f = JpegFile(path, "")
        f.generate_signature = mock.Mock(return_value="signature")
        f.generate_payload = mock.Mock(return_value="payload")
        f.sign(None, None)

        exif = piexif.load(path)
        self.assertEqual(exif["0th"][piexif.ImageIFD.HostComputer], b"payload")

    def test_verify_no_signature(self):

        path = self.copy_for_work("test.jpg")

        f = JpegFile(path, "")
        self.assertFalse(f.verify())

    def test_verify(self):

        path = self.copy_for_work("test-signed.jpg")

        f = JpegFile(path, "")
        f.verify_signature = mock.Mock(return_value=True)
        self.assertTrue(f.verify())
