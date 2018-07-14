from ..base import FFmpegFile


class Mp4File(FFmpegFile):

    SUPPORTED_TYPES = ("video/mp4",)

    def _get_suffix(self) -> str:
        return "mp4"

    def _get_metadata_key(self) -> str:
        return "comment"
