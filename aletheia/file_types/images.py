import json

import pyexiv2
from PIL import Image

from .base import File


class JpegFile(File):

    SUPPORTED_TYPES = ("image/jpeg",)

    def get_raw_data(self):
        with Image.open(self.path) as im:
            return im.tobytes()

    def sign(self, private_key, public_key_url):
        """
        Use Pillow to capture the raw image data, generate a signature from it,
        and then use exiv2 to write said signature + where to find the public
        key to the image metadata in the following format:

          {"version": int, "public-key": url, "signature": signature}

        :param private_key     key  The private key used for signing
        :param public_key_url  str  The URL where you're storing the public key

        :return None
        """

        signature = self.generate_signature(private_key)

        self.logger.debug("Signature generated: %s", signature)

        payload = self.generate_payload(public_key_url, signature)

        metadata = pyexiv2.ImageMetadata(self.path)
        metadata.read()
        metadata["Xmp.plus.ImageCreatorID"] = payload
        metadata.write()

    def verify(self):
        """
        Attempt to verify the origin of an image by checking its local
        signature against the public key listed in the file.
        :return: boolean  ``True`` if verified, `False`` if not.
        """

        metadata = pyexiv2.ImageMetadata(self.path)
        metadata.read()

        try:
            data = json.loads(metadata["Xmp.plus.ImageCreatorID"].value)
            key_url = data["public-key"]
            signature = data["signature"]
        except (KeyError, json.JSONDecodeError):
            self.logger.error("Invalid format, or no signature found")
            return False

        self.logger.debug("Signature found: %s", signature)

        return self.verify_signature(key_url, signature)
