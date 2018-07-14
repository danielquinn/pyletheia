from ..base import FFMpegFile


class WebmFile(FFMpegFile):

    SUPPORTED_TYPES = ("video/webm",)

    def _get_suffix(self) -> str:
        return "webm"
