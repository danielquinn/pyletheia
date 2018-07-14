from ..base import FFMpegFile


class Mp3File(FFMpegFile):

    SUPPORTED_TYPES = ("audio/mpeg", "audio/mpeg3", "audio/x-mpeg-3")

    def _get_suffix(self):
        return "mp3"
