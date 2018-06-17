import re

from ...exceptions import UnparseableFileError
from ..base import File


class HtmlFile(File):

    SUPPORTED_TYPES = ("text/html",)
    SIGNATURE_REGEX = re.compile(
        r'.*<!-- aletheia:{'
        r'"version":(?P<version>1),'
        r'"public-key":"(?P<public_key>[^"]+)",'
        r'"signature":"(?P<signature>[a-f0-9]{2048})"'
        r'} -->$'
    )

    def __init__(self, *args, **kwargs):
        self.__raw = None
        super().__init__(*args, **kwargs)

    def get_raw_data(self) -> bytes:

        if self.__raw is not None:
            return self.__raw

        with open(self.source, "rb") as f:
            self.__raw = self.SIGNATURE_REGEX.sub(
                "",
                f.read().decode()
            ).encode()

        return self.__raw

    def sign(self, private_key, public_key_url: str) -> None:

        signature = self.generate_signature(private_key)

        self.logger.debug("Signature generated: %s", signature)

        with open(self.source, "wb") as f:
            f.write(self.get_raw_data())
            f.write(("<!-- aletheia:{} -->".format(
                self.generate_payload(public_key_url, signature)
            )).encode())

    def verify(self) -> str:

        with open(self.source) as f:
            m = self.SIGNATURE_REGEX.search(f.read())
            if not m:
                self.logger.warning("Invalid format, or no signature found")
                raise UnparseableFileError

        key_url = m.group("public_key")
        signature = m.group("signature").encode()

        self.logger.debug("Signature found: %s", signature)

        return self.verify_signature(key_url, signature)
