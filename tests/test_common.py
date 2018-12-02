import binascii
import os

from aletheia.common import get_key
from aletheia.exceptions import UnrecognisedKey
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from .base import TestCase


class CommonTestCase(TestCase):

    PRIVATE_KEY_PATH = os.path.join(
        os.path.dirname(__file__), "data", "keys", "private.pem")
    PUBLIC_KEY_OPENSSH_PATH = os.path.join(
        os.path.dirname(__file__), "data", "keys", "public.openssh")
    PUBLIC_KEY_PKCS1_PATH = os.path.join(
        os.path.dirname(__file__), "data", "keys", "public.pkcs1")

    # This is b"test" signed with the private key
    SIGNATURE = binascii.unhexlify(
        b"5655c1ac907da18177b965aeaf93ffdc7f13da2c3bd9a1da98c374d21b2ba228adc"
        b"9cd53db7b875a8e3bba627abb10143538031db6709c6aaf6c78d05580a5ce9c6301"
        b"871a430850647d823ba3bcbaab6648a594d81345c72a12714a912795debbeaa9dff"
        b"1d7995c866c552e74fabbc4ea95d4f0c1746d6c7ab247131b539bd62615d333c914"
        b"70d91055fff2bc5c859afb9ab69a17aedcfce62416eab66c808dfb4390cac6de239"
        b"631a8a56a9c7b85ed50dab44b9d474e4f9a0af5d585f1d76155f8e0bf1da63212fa"
        b"e3de599bfd27feeb63e173990197951e1d60d12c5ae11fd3df35ac4c7efd095a473"
        b"86b1941a18602024637a6be5a69e27e65e1b4331e5df02bdd90999730c7d6f6e342"
        b"e13bbd2160ac6e15c59d67f2a901c75ad591ddaed67a972b32e41cb1e1bd14abf10"
        b"c9fbe481355763daf68874b36c5b3be7775d0b73f7f17f9f683225ea06eb5d9db46"
        b"d1079a5ff5991e381e88f644fe2d0a541b3a352e5f2bc64f2da9279e7584cec4bae"
        b"aae8cd9f87e286d3323c91c7d010a6618ae23c46f79c062ae8d136e4d7fc9f6832b"
        b"514cccddfe2a98e2ac3e059b3c4bc0dcea3927695f9151ee8f2d678c410cc867688"
        b"1bed745e2b1a7fa826832cacda400a29af4891ba630ab905261c855f21521449dcf"
        b"4f473ecd097313c8ca61b8c4763909602c89dd5ba528ef82cd3140fb49aa94a0f12"
        b"f03e644f9a4948f887ae9d180e049104d33c94051f2096d2194d322e0ee56bd18af"
        b"22c67ba30ac601c74fb60d045eb08d88e5c521730b393c8df99ebc000c8136130e1"
        b"dcd5d1790c6fdad5b66064dd2a0846eb2c83346eb542c0ea164b2ee84b14f7f038c"
        b"f106728cf6187fa12b5961133d3914da107a3c0fdfac534877f2e9e76698349acb7"
        b"2d89f1304fa6259d20fa7c23b8a82ce68a67b10571b46df13a36057c4312f572e75"
        b"571b7c7ab65268bd199017969aeaf33a5947f234f0f620be9d6b01c91739b43cb10"
        b"145b73e82a28272ac1a08166445f166e58efe2e589359b4b73908849bbf7321ccaf"
        b"ef220d91d6b4da53b41f6e8c8b6bc7e702b0a119aee0d08d374eb60e06bbc75e860"
        b"b0f25dad6ba0cda0ce39f9d89a01cf6b77d551e9672ccd207b589c7428fc2248cce"
        b"7ed20daac4a50cb3ba19065ee9b4a3695f6a46853c1ceece9a75de8d1e418515bc3"
        b"af5ef28367db7da7917ec9f811dafb17f45f6b47162c7b5a3061c6abcfd4f735765"
        b"4949202f849c4ad0227e40208cba0805096e88105f7e231b24beb2f05acfb517585"
        b"fa73b350dd45d71d8ae4e5a368c3f7ed5d9bfc872dba7c0ab0f368fbb44694d8871"
        b"39bec6e381333f92b22231786a90b477fe9ec217727dbca9225bc1ced19fe3e4f8c"
        b"8162a60d273e4c5855194b8390d384f423742370731f992824b9a755d1c22f0dcdc"
        b"13a291bd1aca9aa8304eaf61075e9b7fdbf6da"
    )

    def test_get_key_private(self):
        with open(self.PRIVATE_KEY_PATH, "rb") as f:
            self.assertTrue(get_key(f.read()))

    def test_get_key_public_pkcs1(self):
        with open(self.PUBLIC_KEY_PKCS1_PATH, "rb") as f:
            self.assertTrue(get_key(f.read()))

    def test_get_key_public_openssh(self):
        with open(self.PUBLIC_KEY_OPENSSH_PATH, "rb") as f:
            self.assertTrue(get_key(f.read()))

    def test_public_keys_are_equivalent(self):

        with open(self.PUBLIC_KEY_OPENSSH_PATH, "rb") as f:
            openssh = get_key(f.read())

        with open(self.PUBLIC_KEY_PKCS1_PATH, "rb") as f:
            pkcs1 = get_key(f.read())

        _padding = padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        )
        algorithm = hashes.SHA256()

        self.assertIsNone(
            pkcs1.verify(self.SIGNATURE, b"test", _padding, algorithm))
        self.assertIsNone(
            openssh.verify(self.SIGNATURE, b"test", _padding, algorithm))

    def test_get_key_unknown(self):
        self.assertRaises(UnrecognisedKey, get_key, b"asdf")
