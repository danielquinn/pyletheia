import os
from hashlib import md5
from unittest import mock

import piexif
from PIL import Image

from aletheia.file_types import JpegFile

from ..base import TestCase


class JpegTestCase(TestCase):

    def test_get_raw_data_from_path(self):
        unsigned = os.path.join(self.DATA, "test.jpg")
        self.assertEqual(
            md5(JpegFile(unsigned, "").get_raw_data()).hexdigest(),
            "cc96a1bff6c259f0534f191e83cfdf0e"
        )

    def test_get_raw_data_from_image(self):
        im = Image.open(os.path.join(self.DATA, "test.jpg"))
        self.assertEqual(
            md5(JpegFile(im, "").get_raw_data()).hexdigest(),
            "cc96a1bff6c259f0534f191e83cfdf0e"
        )

    def test_sign_from_path(self):

        path = self.copy_for_work("test.jpg")

        f = JpegFile(path, "")
        f.generate_signature = mock.Mock(return_value="signature")
        f.generate_payload = mock.Mock(return_value="payload")
        f.sign(None, None)

        exif = piexif.load(path)
        self.assertEqual(exif["0th"][piexif.ImageIFD.HostComputer], b"payload")

    def test_sign_from_image(self):

        path = self.copy_for_work("test.jpg")
        im = Image.open(path)

        f = JpegFile(im, "")
        f.generate_signature = mock.Mock(return_value="signature")
        f.generate_payload = mock.Mock(return_value="payload")
        signed_im = f.sign(None, None)

        exif = piexif.load(signed_im.info["exif"])
        self.assertEqual(exif["0th"][piexif.ImageIFD.HostComputer], b"payload")

    def test_verify_from_path_no_signature(self):

        path = self.copy_for_work("test.jpg")

        f = JpegFile(path, "")
        self.assertFalse(f.verify())

    def test_verify_from_path(self):

        path = self.copy_for_work("test-signed.jpg")

        f = JpegFile(path, "")
        f.verify_signature = mock.Mock(return_value=True)
        self.assertTrue(f.verify())

    def test_verify_from_image_no_signature(self):

        path = self.copy_for_work("test.jpg")
        im = Image.open(path)

        f = JpegFile(im, "")
        self.assertFalse(f.verify())

    def test_verify_from_image(self):

        path = self.copy_for_work("test-signed.jpg")
        im = Image.open(path)

        f = JpegFile(im, "")
        f.verify_signature = mock.Mock(return_value=True)
        self.assertTrue(f.verify())
