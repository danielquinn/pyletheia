#
#   $ aletheia generate
#   $ aletheia sign /path/to/file public-key-url
#   $ aletheia verify /path/to/file
#

import argparse
import os

from cryptography.exceptions import InvalidSignature
from termcolor import cprint

from aletheia.aletheia import Aletheia
from aletheia.exceptions import (
    InvalidURLError,
    PublicKeyNotExistsError,
    UnknownFileTypeError,
    UnparseableFileError
)
from aletheia.utils import generate, sign, verify


class Command:

    def __init__(self):

        self.parser = argparse.ArgumentParser(prog="aletheia")
        self.parser.set_defaults(func=self.parser.print_help)
        subparsers = self.parser.add_subparsers(dest="subcommand")

        subparsers.add_parser(
            "generate",
            help="Generate a public/private key pair for use in signing & 3rd "
                 "party verification. (Do this first)"
        )

        parser_sign = subparsers.add_parser("sign", help="Sign a file")
        parser_sign.add_argument("path")
        parser_sign.add_argument(
            "url", nargs="?", default=os.getenv("ALETHEIA_PUBLIC_KEY_URL"))

        parser_verify = subparsers.add_parser(
            "verify", help="Verify the origin of a file")
        parser_verify.add_argument("path")

    @classmethod
    def run(cls):

        instance = cls()

        args = instance.parser.parse_args()

        if args.subcommand:
            return getattr(instance, args.subcommand)(args)

        instance.parser.print_help()
        return 0

    @classmethod
    def generate(cls, *args):

        private = Aletheia().private_key_path
        if os.path.exists(private):
            cprint(
                "It looks like you already have a key setup at {}.\n"
                "Exiting prematurely just to be safe.".format(private),
                "yellow"
            )
            return 1

        cprint("\n  🔑  Generating private/public key pair...", "green")
        generate()
        cprint("""
            All finished!

            You now have two files: aletheia.pem (your private key) and
            aletheia.pub (your public key).  Keep the former private, and share
            the latter far-and-wide.  Importantly, place your public key at a
            publicly accessible URL so that when you sign a file with your
            private key, it can be verified by reading the public key at that
            URL.
        """.replace("          ", ""), "green")

    @classmethod
    def sign(cls, args):

        if not args.url:
            cprint(
                "\n  ✖️  You must specify the public key URL either in the "
                "environment as \n  ALETHEIA_PUBLIC_KEY_URL or on the command "
                "line as the second argument.\n",
                "red"
            )
            return 3

        try:
            sign(args.path, args.url)
        except FileNotFoundError:
            cprint(
                "\n  ✖️  Aletheia can't find that file\n",
                "red"
            )
            return 1
        except UnknownFileTypeError:
            cprint(
                "\n  ✖️  Aletheia doesn't know how to sign that file type\n",
                "red"
            )
            return 2
        template = "\n  ✔  {} was signed with your private key\n"
        cprint(template.format(args.path), "green")

        return 0

    @classmethod
    def verify(cls, args):

        try:
            domain = verify(args.path)
        except FileNotFoundError:
            cprint(
                "\n  ✖️  Aletheia can't find that file\n",
                "red"
            )
            return 1
        except UnknownFileTypeError:
            cprint(
                "\n  ✖️  Aletheia doesn't recognise that file type\n",
                "red"
            )
            return 2
        except UnparseableFileError:
            cprint(
                "\n  ✖️  Aletheia can't find a signature in that file\n",
                "red"
            )
            return 3
        except InvalidURLError:
            cprint(
                "\n  ✖️  The public key URL in the file provided is invalid\n",
                "red"
            )
            return 4
        except PublicKeyNotExistsError:
            cprint(
                "\n  ✖️  The specified URL does not contain a public key\n",
                "red"
            )
            return 5
        except InvalidSignature:
            cprint("\n  ✖️  There's something wrong with that file\n", "red")
            return 6

        template = "\n  ✔  The file is verified as having originated at {}\n"
        cprint(template.format(domain), "green")

        return 0


if __name__ == "__main__":
    Command.run()
