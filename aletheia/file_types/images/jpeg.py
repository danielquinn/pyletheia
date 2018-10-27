from .base import ImageFile


class JpegFile(ImageFile):

    SUPPORTED_TYPES = ("image/jpeg",)
