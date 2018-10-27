import json
import subprocess

from ...exceptions import DependencyMissingError, UnparseableFileError
from ..base import File


class ImageFile(File):

    NOT_FOUND_ERROR_MESSAGE = (
        "Handling this file type requires a working installation of exiftool "
        "(https://sno.phy.queensu.ca/~phil/exiftool/) and for the moment, "
        "Aletheia can't find one on this system.  If you're sure it's "
        "installed, make sure that it's callable from the PATH, and if it "
        "isn't installed, you can follow the instructions on the FFmpeg "
        "website for how to do that.  Don't worry, it's pretty easy."
    )

    def get_raw_data(self) -> bytes:

        with open(self.source, "rb") as f:
            try:
                proc = subprocess.Popen(
                    ("exiftool", "-all=", "-"),
                    stdin=f,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                if proc.wait():
                    raise RuntimeError(proc.stderr.read())
                return proc.stdout.read()

            except FileNotFoundError:
                raise DependencyMissingError(self.NOT_FOUND_ERROR_MESSAGE)

            except RuntimeError as e:
                raise UnparseableFileError(e)

    def sign(self, private_key, public_key_url: str) -> None:

        signature = self.generate_signature(private_key)

        self.logger.debug("Signature generated: %s", signature)

        payload = self.generate_payload(public_key_url, signature)

        try:

            proc = subprocess.Popen(
                (
                    "exiftool",
                    "-ImageSupplierImageID={}".format(payload),
                    "-overwrite_original",
                    self.source
                ),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            if proc.wait():
                raise RuntimeError(proc.stderr.read())

        except RuntimeError as e:
            raise UnparseableFileError(e)

    def verify(self) -> str:
        """
        Attempt to verify the origin of an image by checking its local
        signature against the public key listed in the file.
        """

        with open(self.source, "rb") as f:

            try:

                proc = subprocess.Popen(
                    (
                        "exiftool",
                        "-s", "-s", "-s",
                        "-ImageSupplierImageID",
                        "-"
                    ),
                    stdin=f,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                if proc.wait():
                    raise RuntimeError(proc.stderr.read())

                data = json.loads(proc.stdout.read().decode())
                key_url = data["public-key"]
                signature = data["signature"]

            except FileNotFoundError:
                raise DependencyMissingError(self.NOT_FOUND_ERROR_MESSAGE)

            except RuntimeError as e:
                raise UnparseableFileError(e)

            except (KeyError, json.JSONDecodeError):
                self.logger.warning("Invalid format, or no signature found")
                raise UnparseableFileError()

        self.logger.debug("Signature found: %s", signature)

        return self.verify_signature(key_url, signature)
