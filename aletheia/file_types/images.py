import json

import pyexiv2
from cryptography.exceptions import InvalidSignature
from PIL import Image

from .base import File


class JpegFile(File):

    SCHEMA_VERSION = 1
    SUPPORTED_TYPES = ("image/jpeg",)

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

        with Image.open(self.path) as im:
            signature = self._generate_signature(private_key, im.tobytes())

        # self.logger.debug("Signature generated: %s", signature)

        payload = json.dumps({
            "version": self.SCHEMA_VERSION,
            "public-key": public_key_url,
            "signature": signature.decode()
        }, separators=(",", ":"))

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

        with Image.open(self.path) as im:
            try:
                self._verify_signature(
                    self._get_public_key(key_url),
                    signature.encode("utf-8"),
                    im.tobytes()
                )
                return True
            except InvalidSignature:
                self.logger.error("Bad signature")
                return False
