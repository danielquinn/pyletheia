from ...exceptions import UnparseableFileError
from ..base import File


class PlainTextFile(File):

    SIGNATURE_WRITE_TEMPLATE = None
    SIGNATURE_REGEX = None

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

    def sign(self, private_key, domain: str) -> None:

        signature = self.generate_signature(private_key)

        self.logger.debug("Signature generated: %s", signature)

        with open(self.source, "wb") as f:
            f.write(self.get_raw_data())
            f.write((self.SIGNATURE_WRITE_TEMPLATE.format(
                self.generate_payload(domain, signature)
            )).encode())

    def verify(self) -> str:

        with open(self.source) as f:
            m = self.SIGNATURE_REGEX.search(f.read())
            if not m:
                self.logger.warning("Invalid format, or no signature found")
                raise UnparseableFileError

        version = int(m.group("version"))
        domain = m.group("domain")
        signature = m.group("signature").encode()

        self.check_schema_version(version)

        self.logger.debug("Signature found: %s", signature)

        return self.verify_signature(domain, signature)
