import textwrap
import os
from typing import List
from unittest import mock

from aletheia.exceptions import (
    PublicKeyNotExistsError,
    UnacceptableLocationError
)
from aletheia.file_types import (
    GifFile,
    HtmlFile,
    JpegFile,
    MarkdownFile,
    MkvFile,
    Mp3File,
    Mp4File,
    PngFile,
    WebmFile
)
from aletheia.file_types.base import File
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from requests.exceptions import RequestException

from ..base import TestCase


def get_dns_friendly_key() -> List[bytes]:
    """
    Takes the test public key and formats it into a list like you'd expect to
    get back from a domain server holding said key in a TXT record.
    """

    path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "keys",
        "public.openssh"
    )
    with open(path, "rb") as f:
        key = "{}={}".format("aletheia-public-key", f.read().decode().strip())
        return [bytes(__, "utf-8") for __ in textwrap.wrap(key, 255)]


def get_http_friendly_key() -> bytes:

    path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "keys",
        "public.pkcs1"
    )

    with open(path, "rb") as f:
        return f.read()


def get_good_key() -> RSAPublicKey:

    path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "keys",
        "public.pkcs1"
    )
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(
            f.read().strip(),
            backend=default_backend()
        )


class FileTestCase(TestCase):

    GOOD_DNS = mock.Mock(
        response=mock.Mock(
            answer=[[mock.Mock(strings=get_dns_friendly_key())]]
        )
    )
    GOOD_HTTP = mock.Mock(content=get_http_friendly_key(), status_code=200)
    GOOD_KEY = get_good_key()

    def test_build_html(self):
        self.assertIsInstance(
            File.build(self._generate_path("html"), self.scratch),
            HtmlFile
        )

    def test_build_gif(self):
        self.assertIsInstance(
            File.build(self._generate_path("gif"), self.scratch),
            GifFile
        )

    def test_build_jpg(self):
        self.assertIsInstance(
            File.build(self._generate_path("jpg"), self.scratch),
            JpegFile
        )

    def test_build_png(self):
        self.assertIsInstance(
            File.build(self._generate_path("png"), self.scratch),
            PngFile
        )

    def test_build_mp3(self):
        self.assertIsInstance(
            File.build(self._generate_path("mp3"), self.scratch),
            Mp3File
        )

    def test_build_mkv(self):
        self.assertIsInstance(
            File.build(self._generate_path("mkv"), self.scratch),
            MkvFile
        )

    def test_build_mp4(self):
        self.assertIsInstance(
            File.build(self._generate_path("mp4"), self.scratch),
            Mp4File
        )

    def test_build_webm(self):
        self.assertIsInstance(
            File.build(self._generate_path("webm"), self.scratch),
            WebmFile
        )

    def test_get_subclasses(self):
        self.assertEqual(
            set(File.get_subclasses()),
            {
                HtmlFile,
                GifFile,
                JpegFile,
                PngFile,
                MarkdownFile,
                MkvFile,
                Mp3File,
                Mp4File,
                WebmFile
            }
        )

    def test_verify_signature(self):

        f = File("/dev/null", self.scratch)
        f._get_public_key = mock.Mock(verify=mock.Mock())
        f.get_raw_data = mock.Mock()

        # example.com
        self.assertEqual(
            f.verify_signature("example.com", b""),
            "example.com"
        )

        # International domain names like ♡.com
        self.assertEqual(
            f.verify_signature("xn--c6h.com", b""),
            "xn--c6h.com"
        )

    def test_verify_signature_bad_domain(self):

        f = File("/dev/null", self.scratch)

        # An empty domain shouldn't work
        self.assertRaises(
            UnacceptableLocationError, f.verify_signature, "", b"")

        # Bad domains shouldn't work
        self.assertRaises(
            UnacceptableLocationError, f.verify_signature, "not a domain", b"")

        # Un-translated international domains shouldn't work
        self.assertRaises(
            UnacceptableLocationError, f.verify_signature, "♡.com", b"")

    @mock.patch("aletheia.file_types.base.dns.resolver.query", side_effect=PublicKeyNotExistsError)
    @mock.patch("aletheia.file_types.base.requests.get", side_effect=RequestException)
    @mock.patch("aletheia.file_types.base.get_key", return_value=GOOD_KEY)
    def test__get_public_key_no_dns_no_http(self, m_get_key, m_requests, m_dns):
        self.assertRaises(
            PublicKeyNotExistsError,
            File("/dev/null", self.scratch)._get_public_key,
            "example.com"
        )
        self.assertEqual(m_get_key.call_count, 0)
        self.assertEqual(m_requests.call_count, 1)
        self.assertEqual(m_dns.call_count, 1)

    @mock.patch("aletheia.file_types.base.dns.resolver.query", return_value=GOOD_DNS)
    @mock.patch("aletheia.file_types.base.requests.get", side_effect=RequestException)
    @mock.patch("aletheia.file_types.base.get_key", return_value=GOOD_KEY)
    def test__get_public_key_yes_dns_no_http(self, m_get_key, m_requests, m_dns):
        self.assertEqual(File("/dev/null", self.scratch)._get_public_key("example.com"), self.GOOD_KEY)
        self.assertEqual(m_get_key.call_count, 1)
        self.assertEqual(m_requests.call_count, 0)
        self.assertEqual(m_dns.call_count, 1)

    @mock.patch("aletheia.file_types.base.dns.resolver.query", side_effect=PublicKeyNotExistsError)
    @mock.patch("aletheia.file_types.base.requests.get", return_value=GOOD_HTTP)
    @mock.patch("aletheia.file_types.base.get_key", return_value=GOOD_KEY)
    def test__get_public_key_no_dns_yes_http(self, m_get_key, m_requests, m_dns):
        self.assertEqual(File("/dev/null", self.scratch)._get_public_key("example.com"), self.GOOD_KEY)
        self.assertEqual(m_get_key.call_count, 1)
        self.assertEqual(m_requests.call_count, 1)
        self.assertEqual(m_dns.call_count, 1)

    @mock.patch("aletheia.file_types.base.dns.resolver.query", return_value=GOOD_DNS)
    @mock.patch("aletheia.file_types.base.requests.get", return_value=GOOD_HTTP)
    @mock.patch("aletheia.file_types.base.get_key", return_value=GOOD_KEY)
    def test__get_public_key_yes_dns_yes_http(self, m_get_key, m_requests, m_dns):
        self.assertEqual(File("/dev/null", self.scratch)._get_public_key("example.com"), self.GOOD_KEY)
        self.assertEqual(m_get_key.call_count, 1)
        self.assertEqual(m_requests.call_count, 0)
        self.assertEqual(m_dns.call_count, 1)

    @mock.patch("aletheia.file_types.base.dns.resolver.query", return_value=GOOD_DNS)
    @mock.patch("aletheia.file_types.base.requests.get", side_effect=RequestException)
    @mock.patch("aletheia.file_types.base.get_key", return_value=GOOD_KEY)
    def test__get_public_key_cache_works(self, m_get_key, m_requests, m_dns):

        f = File("/dev/null", self.scratch)

        self.assertEqual(f._get_public_key("example.com"), self.GOOD_KEY)
        self.assertEqual(m_get_key.call_count, 1)
        self.assertEqual(m_requests.call_count, 0)
        self.assertEqual(m_dns.call_count, 1)

        self.assertEqual(f._get_public_key("example.com"), self.GOOD_KEY)
        self.assertEqual(m_get_key.call_count, 2)
        self.assertEqual(m_requests.call_count, 0)
        self.assertEqual(m_dns.call_count, 1)

        self.assertEqual(f._get_public_key("example.com", use_cache=False), self.GOOD_KEY)
        self.assertEqual(m_get_key.call_count, 3)
        self.assertEqual(m_requests.call_count, 0)
        self.assertEqual(m_dns.call_count, 2)

    @mock.patch("aletheia.file_types.base.dns.resolver.query", return_value=GOOD_DNS)
    @mock.patch("aletheia.file_types.base.requests.get", side_effect=RequestException)
    @mock.patch("aletheia.file_types.base.get_key", return_value=GOOD_KEY)
    def test__get_public_key_cache_invalidates(self, m_get_key, m_requests, m_dns):

        f = File("/dev/null", self.scratch)
        f.CACHE_TIME = 0

        self.assertEqual(f._get_public_key("example.com"), self.GOOD_KEY)
        self.assertEqual(m_get_key.call_count, 1)
        self.assertEqual(m_requests.call_count, 0)
        self.assertEqual(m_dns.call_count, 1)

        self.assertEqual(f._get_public_key("example.com"), self.GOOD_KEY)
        self.assertEqual(m_get_key.call_count, 2)
        self.assertEqual(m_requests.call_count, 0)
        self.assertEqual(m_dns.call_count, 2)

    def _generate_path(self, type_: str) -> str:
        return os.path.join(self.DATA, "original", "test.{}".format(type_))
