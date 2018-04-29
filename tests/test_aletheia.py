import os
import shutil
import test.support
import unittest

from aletheia.aletheia import Aletheia


class AletheiaTestCase(unittest.TestCase):

    SCRATCH = "/tmp/aletheia-tests"

    def setUp(self):

        self.env = test.support.EnvironmentVarGuard()
        self.env["HOME"] = self.SCRATCH

        os.makedirs(self.env["HOME"], exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.SCRATCH, ignore_errors=True)

    def test___init___defaults(self):

        with self.env:
            aletheia = Aletheia()

        home = "{}/.config/aletheia".format(self.SCRATCH)
        self.assertEqual(
            aletheia.private_key_path, "{}/aletheia.pem".format(home))
        self.assertEqual(
            aletheia.public_key_path, "{}/aletheia.pub".format(home))
        self.assertEqual(
            aletheia.public_key_cache, "{}/public-keys".format(home))

    def test___init___with_values(self):

        with self.env:
            aletheia = Aletheia(
                private_key_path="alpha",
                public_key_path="bravo",
                cache_dir="charlie"
            )

        self.assertEqual(aletheia.private_key_path, "alpha")
        self.assertEqual(aletheia.public_key_path, "bravo")
        self.assertEqual(aletheia.public_key_cache, "charlie")

    def test_generate(self):

        with self.env:
            Aletheia().generate()

        home = os.path.join(self.SCRATCH, ".config", "aletheia")
        self.assertTrue(os.path.exists(os.path.join(home, "aletheia.pem")))
        self.assertTrue(os.path.exists(os.path.join(home, "aletheia.pub")))

        with open(os.path.join(home, "aletheia.pem")) as f:
            self.assertIn("BEGIN", f.read())

        with open(os.path.join(home, "aletheia.pub")) as f:
            self.assertIn("BEGIN", f.read())

    def test_sign_file_doesnt_exist(self):

        with self.env:
            aletheia = Aletheia()

        self.assertRaises(
            FileNotFoundError, aletheia.sign, "/dev/null/nowhere", "")

    def test_verify_file_doesnt_exist(self):

        with self.env:
            aletheia = Aletheia()

        self.assertRaises(
            FileNotFoundError, aletheia.verify, "/dev/null/nowhere")

    def test__get_private_key_in_environment(self):

        private_key_path = os.path.join(
            os.path.dirname(__file__), "data", "key.pem")
        with open(private_key_path) as f:
            self.env["ALETHEIA_PRIVATE_KEY"] = f.read()

        with self.env:
            aletheia = Aletheia()
            self.assertIsNotNone(aletheia._get_private_key())

    def test__get_private_key_in_file(self):
        with self.env:
            aletheia = Aletheia(private_key_path=os.path.join(
                os.path.dirname(__file__), "data", "key.pem"))
            self.assertIsNotNone(aletheia._get_private_key())

    def test__get_private_key_doesnt_exist(self):
        with self.env:
            self.assertRaises(RuntimeError, Aletheia()._get_private_key)
