import re

from .base import PlainTextFile


class MarkdownFile(PlainTextFile):

    SUPPORTED_TYPES = ("text/markdown",)
    SIGNATURE_WRITE_TEMPLATE = "[//]: # (aletheia:{})"
    SIGNATURE_REGEX = re.compile(
        r'.*\[//\]: # \(aletheia:{'
        r'"version":(?P<version>1),'
        r'"public-key":"(?P<public_key>[^"]+)",'
        r'"signature":"(?P<signature>[a-f0-9]{2048})"'
        r'}\)$'
    )

