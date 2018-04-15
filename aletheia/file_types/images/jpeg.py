import json
from io import BytesIO

import piexif
from PIL import Image
from PIL.JpegImagePlugin import JpegImageFile

from ..base import File


class JpegFile(File):

    SUPPORTED_TYPES = ("image/jpeg",)

    def get_raw_data(self):

        if isinstance(self.source, JpegImageFile):
            return self.source.tobytes()

        with Image.open(self.source) as im:
            return im.tobytes()

    def sign(self, private_key, public_key_url):
        """
        Use Pillow to capture the raw image data, generate a signature from it,
        and then use piexif to write said signature + where to find the public
        key to the image metadata in the following format:

          {"version": int, "public-key": url, "signature": signature}

        :param private_key     key  The private key used for signing
        :param public_key_url  str  The URL where you're storing the public key

        :return None if we're operating on a file. If we're working with an
                Image object, we return the signed object.
        """

        signature = self.generate_signature(private_key)

        self.logger.debug("Signature generated: %s", signature)

        payload = self.generate_payload(public_key_url, signature)

        if isinstance(self.source, JpegImageFile):
            return self._sign_inline(payload)

        exif = piexif.load(self.source)
        exif["0th"][piexif.ImageIFD.HostComputer] = payload
        piexif.insert(piexif.dump(exif), self.source)

    def _sign_inline(self, payload):
        """
        This isn't the most elegant way to do this, but I don't know of a
        better one.  The problem is that Pillow doesn't appear to have a means
        of editing EXIF data in-place, rather you have to write the stuff to
        the image object during the ``.save()`` step, so to work around this,
        we're just writing to memory and then re-opening it to return the
        newly-tagged object.

        Note that doing this subjects us to JPEG degradation as it's a lossy
        compression algorithm.  Better ideas are always welcome.

        :param payload: The JSON string we're writing to the image
        :return: A Pillow ``Image`` object with the new EXIF headers attached.
        """

        exif = {"0th": {}}
        if "exif" in self.source.info:
            exif = piexif.load(self.source.info.get("exif"))

        temp = BytesIO()
        exif["0th"][piexif.ImageIFD.HostComputer] = payload
        self.source.save(
            temp,
            "jpeg",
            quality="keep",
            subsampling="keep",
            qtables="keep",
            exif=piexif.dump(exif)
        )
        temp.seek(0)
        return Image.open(temp)

    def verify(self):
        """
        Attempt to verify the origin of an image by checking its local
        signature against the public key listed in the file.
        :return: boolean  ``True`` if verified, `False`` if not.
        """

        if isinstance(self.source, JpegImageFile):
            if "exif" not in self.source.info:
                self.logger.error("No EXIF data found in Image instance")
                return False
            exif = piexif.load(self.source.info["exif"])
        else:
            exif = piexif.load(self.source)

        try:
            data = json.loads(
                exif["0th"][piexif.ImageIFD.HostComputer].decode("utf-8"))
            key_url = data["public-key"]
            signature = data["signature"]
        except (KeyError, json.JSONDecodeError):
            self.logger.error("Invalid format, or no signature found")
            return False

        self.logger.debug("Signature found: %s", signature)

        return self.verify_signature(key_url, signature)
