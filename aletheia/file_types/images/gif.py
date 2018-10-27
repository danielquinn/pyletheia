from .base import ImageFile


class GifFile(ImageFile):
    """
    It's pronounced "jif", like the peanut butter!
    """

    SUPPORTED_TYPES = ("image/gif",)
