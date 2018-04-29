import json

import piexif
import PIL.Image

from ...exceptions import UnparseableFileError
from ..base import File


class JpegFile(File):

    SUPPORTED_TYPES = ("image/jpeg",)

    def get_raw_data(self):
        with PIL.Image.open(self.source) as im:
            return im.tobytes()

    def sign(self, private_key, public_key_url):
        """
        Use Pillow to capture the raw image data, generate a signature from it,
        and then use piexif to write said signature + where to find the public
        key to the image metadata in the following format:

          {"version": int, "public-key": url, "signature": signature}

        :param private_key     key  The private key used for signing
        :param public_key_url  str  The URL where you're storing the public key
        """

        signature = self.generate_signature(private_key)

        self.logger.debug("Signature generated: %s", signature)

        payload = self.generate_payload(public_key_url, signature)

        exif = piexif.load(self.source)
        exif["0th"][piexif.ImageIFD.HostComputer] = payload
        piexif.insert(piexif.dump(exif), self.source)

    def verify(self):
        """
        Attempt to verify the origin of an image by checking its local
        signature against the public key listed in the file.
        :return: boolean  ``True`` if verified, `False`` if not.
        """

        exif = piexif.load(self.source)

        try:
            data = json.loads(
                exif["0th"][piexif.ImageIFD.HostComputer].decode("utf-8"))
            key_url = data["public-key"]
            signature = data["signature"]
        except (KeyError, json.JSONDecodeError):
            self.logger.warning("Invalid format, or no signature found")
            raise UnparseableFileError()

        self.logger.debug("Signature found: %s", signature)

        return self.verify_signature(key_url, signature)
