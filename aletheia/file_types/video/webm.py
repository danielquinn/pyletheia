from ..base import FFmpegFile


class WebmFile(FFmpegFile):

    SUPPORTED_TYPES = ("video/webm",)

    def _get_suffix(self) -> str:
        return "webm"
