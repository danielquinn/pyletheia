import json
import subprocess

from mutagen.id3 import ID3, TPUB

from ...exceptions import UnparseableFileError
from ..base import LargeFile


class Mp3File(LargeFile):

    SCHEMA_VERSION = 1
    SUPPORTED_TYPES = ("audio/mpeg",)

    def get_raw_data(self):
        return subprocess.Popen(
            (
                "ffmpeg",
                "-i", self.source,
                "-vn",
                "-codec:a", "copy",
                "-map_metadata", "-1",
                "-f", "mp3",
                "-"
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        ).stdout

    def sign(self, private_key, public_key_url):

        signature = self.generate_signature(private_key)

        self.logger.debug("Signature generated: %s", signature)

        payload = self.generate_payload(public_key_url, signature)

        audio = ID3(self.source)
        audio.add(TPUB(encoding=3, text=payload))
        audio.save()

    def verify(self):

        audio = ID3(self.source)

        try:

            payload = json.loads(audio.get("TPUB")[0])

            self.logger.debug("Found payload: %s", payload)

            key_url = payload["public-key"]
            signature = payload["signature"]

        except (ValueError, TypeError, IndexError, json.JSONDecodeError):
            self.logger.error("Invalid format, or no signature found")
            raise UnparseableFileError()

        return self.verify_signature(key_url, signature)
