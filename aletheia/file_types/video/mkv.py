from ..base import FFMpegFile


class MkvFile(FFMpegFile):

    SUPPORTED_TYPES = ("video/x-matroska",)

    def _get_suffix(self) -> str:
        return "mkv"
