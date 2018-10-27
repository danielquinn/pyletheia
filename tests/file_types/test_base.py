import os

from aletheia.file_types import (
    GifFile,
    HtmlFile,
    JpegFile,
    MkvFile,
    Mp3File,
    Mp4File,
    PngFile,
    WebmFile
)
from aletheia.file_types.base import File

from ..base import TestCase


class FileTestCase(TestCase):

    def test_build_html(self):
        self.assertIsInstance(
            File.build(self._generate_path("html"), self.SCRATCH),
            HtmlFile
        )

    def test_build_gif(self):
        self.assertIsInstance(
            File.build(self._generate_path("gif"), self.SCRATCH),
            GifFile
        )

    def test_build_jpg(self):
        self.assertIsInstance(
            File.build(self._generate_path("jpg"), self.SCRATCH),
            JpegFile
        )

    def test_build_png(self):
        self.assertIsInstance(
            File.build(self._generate_path("png"), self.SCRATCH),
            PngFile
        )

    def test_build_mp3(self):
        self.assertIsInstance(
            File.build(self._generate_path("mp3"), self.SCRATCH),
            Mp3File
        )

    def test_build_mkv(self):
        self.assertIsInstance(
            File.build(self._generate_path("mkv"), self.SCRATCH),
            MkvFile
        )

    def test_build_mp4(self):
        self.assertIsInstance(
            File.build(self._generate_path("mp4"), self.SCRATCH),
            Mp4File
        )

    def test_build_webm(self):
        self.assertIsInstance(
            File.build(self._generate_path("webm"), self.SCRATCH),
            WebmFile
        )

    def test_get_subclasses(self):
        self.assertEqual(
            set(File.get_subclasses()),
            {
                HtmlFile,
                GifFile,
                JpegFile,
                PngFile,
                MkvFile,
                Mp3File,
                Mp4File,
                WebmFile
            }
        )

    def _generate_path(self, type_: str) -> str:
        return os.path.join(self.DATA, "original", "test.{}".format(type_))
