import json
import subprocess

import mutagen

from ...exceptions import UnparseableFileError
from ..base import LargeFile


class Mp4File(LargeFile):

    SCHEMA_VERSION = 1
    SUPPORTED_TYPES = ("video/mp4",)

    def get_raw_data(self):
        with open(self.source, "rb") as f:
            return subprocess.Popen(
                ("exiftool", "-all=", "-"),
                stdin=f,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            ).stdout

    def sign(self, private_key, public_key_url):

        signature = self.generate_signature(private_key)

        self.logger.debug("Signature generated: %s", signature)

        payload = self.generate_payload(public_key_url, signature)

        mp4 = mutagen.File(self.source)
        mp4["\xa9too"] = payload  # We use the "Encoded by" tag
        mp4.save()

    def verify(self):

        mp4 = mutagen.File(self.source)

        try:

            payload = json.loads(mp4.get("\xa9too")[0])

            self.logger.debug("Found payload: %s", payload)

            key_url = payload["public-key"]
            signature = payload["signature"]

        except (ValueError, TypeError, IndexError, json.JSONDecodeError):
            self.logger.error("Invalid format, or no signature found")
            raise UnparseableFileError()

        return self.verify_signature(key_url, signature)
