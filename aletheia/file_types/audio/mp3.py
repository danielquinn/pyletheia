from ..base import FFmpegFile


class Mp3File(FFmpegFile):

    SUPPORTED_TYPES = ("audio/mpeg", "audio/mpeg3", "audio/x-mpeg-3")

    def _get_suffix(self):
        return "mp3"
