import re

from ...exceptions import UnparseableFileError
from .base import PlainTextFile


class HtmlFile(PlainTextFile):

    SUPPORTED_TYPES = ("text/html",)
    SIGNATURE_WRITE_TEMPLATE = "<!-- aletheia:{} -->"
    SIGNATURE_REGEX = re.compile(
        r'.*<!-- aletheia:{'
        r'"version":(?P<version>1),'
        r'"public-key":"(?P<public_key>[^"]+)",'
        r'"signature":"(?P<signature>[a-f0-9]{2048})"'
        r'} -->$'
    )

