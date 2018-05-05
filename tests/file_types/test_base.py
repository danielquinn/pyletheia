import os

from aletheia.file_types.base import File
from aletheia.file_types import JpegFile, Mp3File

from ..base import TestCase


class FileTestCase(TestCase):

    def test_build_jpg(self):
        self.assertIsInstance(
            File.build(os.path.join(self.DATA, "test.jpg"), self.SCRATCH),
            JpegFile
        )

    def test_build_mp3(self):
        self.assertIsInstance(
            File.build(os.path.join(self.DATA, "test.mp3"), self.SCRATCH),
            Mp3File
        )

    def test_get_subclasses(self):
        self.assertEqual(set(File.get_subclasses()), {JpegFile, Mp3File})
