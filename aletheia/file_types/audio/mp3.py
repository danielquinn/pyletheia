import json

from mutagen.id3 import ID3, TPUB

from ...exceptions import UnparseableFileError
from ..base import FFMpegFile


class Mp3File(FFMpegFile):

    SCHEMA_VERSION = 1
    SUPPORTED_TYPES = ("audio/mpeg",)

    def sign(self, private_key, public_key_url):

        signature = self.generate_signature(private_key)

        self.logger.debug("Signature generated: %s", signature)

        payload = self.generate_payload(public_key_url, signature)

        mp3 = ID3(self.source)
        mp3.add(TPUB(encoding=3, text=payload))
        mp3.save()

    def verify(self):

        mp3 = ID3(self.source)

        try:

            payload = json.loads(mp3.get("TPUB")[0])

            self.logger.debug("Found payload: %s", payload)

            key_url = payload["public-key"]
            signature = payload["signature"]

        except (ValueError, TypeError, IndexError, json.JSONDecodeError):
            self.logger.error("Invalid format, or no signature found")
            raise UnparseableFileError()

        return self.verify_signature(key_url, signature)
