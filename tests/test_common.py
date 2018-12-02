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
        b"166ccff5c13670c77c68b4017f827967ae81682cbc24f1f37c3f04284759e9cff4b0"
        b"53df252ebcebfa8d71286d9dd59cd3c939a1e3f4a89ba36850373d053b40ece0d047"
        b"ef8a116d16f5e98a623fe7aa583a223d2629a842d55f0b5b3520dd1b0f3de1174153"
        b"edf6d25fac7506c7c75bdbac4580adc0191430b1056c2fc8501827f2d23a3687198a"
        b"4793c636d9e1067eee983103265b1b7425c7b7c01b676407bb09318759b2351bbe9e"
        b"d79b9a14f534e505538f224949905cfc4744049ed728b38eb89deae4222146cbd972"
        b"b4ea0ead9682b382884c3894633e66d3decff1cae9be6229f1ed6a14b6dceef84b5f"
        b"7bd1e930b225810003a7edb260c213106f306cf0c5e42ccade54fcc623ccb7ae033e"
        b"9ed159a1a5bc5a74f74de2b00bfaf6bd7f901c088b45b9993bb71ade7785841d9c05"
        b"b761c7e1b8a7bad2d1560f412d5bc29425882eee64a82ee40905574735d1a92e172b"
        b"6448b1a32e1cde9bfe586d5cfe75bc5b7a080f29503d73d56b02fcafea0520997757"
        b"9f28c3e1fbf7ae18ca70cc9e9a5903b5d84bc8b9e1b4a11bbc1673a4a55732eb7036"
        b"df535a507a7213af89ab839d85d790102be57da34babc6c7f780a34d47b4737be8f9"
        b"ab5625bbe4bd624dc6ef33e34054704afdd2cdedeb8702cc59a37e3d33342fb4ae93"
        b"508bb47a6e52baed1e30aa65d662681f48e38f84d9b5481e0e4c73e31d14a4cef3ce"
        b"d88a736d51c578c2134702931aa552b34ab5dd9aae60c1fc51dedd85448ef8a794d2"
        b"dade51a6c3e894f51ca60b46c50046ad49d2f239565ae0f2c6d70af2d8e795fcb5f0"
        b"e3d42bb30818bc41548017ca8c4e88ac183c36e9768d2ed15178a22cc4c28d5527b0"
        b"b3189ec433e9dfa9def1c316b6be1012af7e724af59385eefe100f6b3c22665fee4e"
        b"074de293677a17e79aa532f0493fb2b5f9371bd29870d867c4c432416832c63e4023"
        b"065e60b09782e626b745d4cc0043098c3f59f2a17c4402951af2a676c8ab2b79fb7d"
        b"998eaa80419b09a76540e7a15a48c78e1da7ee25cc0867026d41e88e6b53b346de75"
        b"1ee04fcc48b721e181ce178c0932f838fe555ab339da84441d10b7d7d12ae738fb6c"
        b"525b8f84cb23f0ad416f9a290688f4335dd0386f64d910ad49c888bc80bab9481052"
        b"15b70b6cc1efdcd8e14c44ebb6849e972e3cae784996dc4c16a4533f3f385c075553"
        b"a146116a6e9a0c0f623b0a613cea3d31b218b3dabd1e0f86a32d0f94d0ea96e1be30"
        b"d4b30df64e89d517f9d98e771f5f843a03c0d80a1340b4d154beeec2b8bd1cf3d80e"
        b"7b982db7bfa4dc1d87ffcf1887235a6ea3666acd4a6965f2bb99fd8f7c996ca3848d"
        b"d9eeb077e35b33b135fbf1d0afe118dc0e2395e83e77d8b8fd10b04cdec781bfd2d7"
        b"2d840864bde32c8b60ecb6fa5b3ea5b24bbe74021198a215a68a013935c1e7b3a030"
        b"eb9c645d"
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
            mgf=padding.MGF1(hashes.SHA512()),
            salt_length=padding.PSS.MAX_LENGTH
        )
        algorithm = hashes.SHA512()

        self.assertIsNone(
            pkcs1.verify(self.SIGNATURE, b"test", _padding, algorithm))
        self.assertIsNone(
            openssh.verify(self.SIGNATURE, b"test", _padding, algorithm))

    def test_get_key_unknown(self):
        self.assertRaises(UnrecognisedKey, get_key, b"asdf")
