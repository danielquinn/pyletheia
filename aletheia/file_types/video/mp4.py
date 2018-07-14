from ..base import FFMpegFile


class Mp4File(FFMpegFile):

    SUPPORTED_TYPES = ("video/mp4",)

    def _get_suffix(self) -> str:
        return "mp4"

    def _get_metadata_key(self) -> str:
        return "comment"
