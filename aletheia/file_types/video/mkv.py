from ..base import FFmpegFile


class MkvFile(FFmpegFile):

    SUPPORTED_TYPES = ("video/x-matroska",)

    def _get_suffix(self) -> str:
        return "mkv"
