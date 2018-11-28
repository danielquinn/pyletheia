#
#   $ aletheia --version
#   $ aletheia public-key [--url] [--format=[pem|openssh]]
#   $ aletheia private-key [--format=[pem|openssh]]
#   $ aletheia generate
#   $ aletheia sign /path/to/file public-key-url
#   $ aletheia verify /path/to/file
#

import argparse
import os
import textwrap

import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from termcolor import cprint

from . import __version__
from .aletheia import Aletheia
from .common import get_key
from .exceptions import (
    DependencyMissingError,
    InvalidURLError,
    PublicKeyNotExistsError,
    UnacceptableLocationError,
    UnknownFileTypeError,
    UnparseableFileError
)
from .utils import generate, sign, verify


class Command:

    def __init__(self):

        self.parser = argparse.ArgumentParser(prog="aletheia")
        self.parser.set_defaults(func=self.parser.print_help)

        self.parser.add_argument(
            "--version", dest="version", action="store_true", default=False)

        subparsers = self.parser.add_subparsers(dest="subcommand")

        subparsers.add_parser(
            "generate",
            help="Generate a public/private key pair for use in signing & 3rd "
                 "party verification. (Do this first)"
        )

        subparsers.add_parser(
            "private-key", help="Get your private key")

        parser_public_key = subparsers.add_parser(
            "public-key", help="Get your public key")
        parser_public_key.add_argument(
            "--url", default=os.getenv("ALETHEIA_PUBLIC_KEY_URL"))
        parser_public_key.add_argument(
            "--format",
            dest="format",
            default="pem",
            choices=("pem", "openssh")
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

        if args.version:
            instance._print_version()
            return 0

        if args.subcommand:
            return getattr(instance, args.subcommand.replace("-", "_"))(args)

        instance.parser.print_help()
        return 0

    @staticmethod
    def _print_version():
        print(".".join(str(_) for _ in __version__))

    @classmethod
    def private_key(cls, args: argparse.Namespace):

        path = Aletheia().private_key_path

        if not os.path.exists(path):
            cls.__print_error(
                "There doesn't appear to be a private key on this system.  "
                "Maybe you need to generate it first?"
            )
            return 1

        with open(path, "rb") as f:
            print(get_key(f.read()).private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ).decode().strip())

        return 0

    @classmethod
    def public_key(cls, args: argparse.Namespace):

        key = None

        if args.url:
            try:
                key = get_key(requests.get(args.url).content)
            except requests.exceptions.RequestException:
                cls.__print_error(
                    "That URL does not appear to contain a public key")
                return 1

        if not key:

            path = Aletheia().public_key_path

            if not os.path.exists(path):
                cls.__print_error(
                    "There doesn't appear to be a public key on this system "
                    "and no URL has been specified.  Maybe you need to "
                    "generate it first?"
                )
                return 1

            with open(path, "rb") as f:
                key = get_key(f.read())

        kwargs = {
            "pem": {
                "encoding": serialization.Encoding.PEM,
                "format": serialization.PublicFormat.PKCS1
            },
            "openssh": {
                "encoding": serialization.Encoding.OpenSSH,
                "format": serialization.PublicFormat.OpenSSH
            }
        }

        print(key.public_bytes(**kwargs[args.format]).decode().strip())

        return 0

    @classmethod
    def generate(cls, args: argparse.Namespace):

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

        fill_kwargs = {
            "initial_indent": "  ",
            "subsequent_indent": "  ",
            "width": 79
        }
        cprint(
            "\n  All finished!\n"
            "\n"
            "{}\n"
            "\n"
            "{}\n"
            "\n"
            "    https://example.com/aletheia.pub\n"
            "\n"
            "  or in a DNS TXT record in this format:\n"
            "\n"
            "    example.com.  3570  IN  TXT  \"aletheia-public-key=ssh-rsa AAAAB3N...\n"  # NOQA: E501
            "\n"
            "{}\n".format(
                textwrap.fill(
                    "You now have two files: aletheia.pem (your private key) "
                    "and aletheia.pub (your public key).  Keep the former "
                    "private, and share the latter far-and-wide.",
                    **fill_kwargs
                ),
                textwrap.fill(
                    "Importantly, you should place your public key on your "
                    "webserver at:",
                    **fill_kwargs
                ),
                textwrap.fill(
                    "Note that if you're planning on using DNS, you would do "
                    "well to implement DNSSec.  If you don't know what this "
                    "means, you should probably stick with using the https:// "
                    "option.",
                    **fill_kwargs
                )
            ),
            "green"
        )

    @classmethod
    def sign(cls, args: argparse.Namespace):

        if not args.url:
            cls.__print_error(
                "You must specify the public key URL either in the "
                "environment as ALETHEIA_PUBLIC_KEY_URL or on the command "
                "line as the second argument."
            )
            return 3

        try:
            sign(args.path, args.url)
        except FileNotFoundError:
            cls.__print_error("Aletheia can't find that file")
            return 1
        except UnknownFileTypeError:
            cls.__print_error(
                "Aletheia doesn't know how to sign that file type")
            return 2
        except DependencyMissingError as e:
            cls.__print_error(str(e))
            return 4
        template = "\n  ✔  {} was signed with your private key\n"
        cprint(template.format(args.path), "green")

        return 0

    @classmethod
    def verify(cls, args: argparse.Namespace):

        try:
            domain = verify(args.path)
        except FileNotFoundError:
            cls.__print_error("Aletheia can't find that file")
            return 1
        except UnknownFileTypeError:
            cls.__print_error("Aletheia doesn't recognise that file type")
            return 2
        except UnparseableFileError:
            cls.__print_error("Aletheia can't find a signature in that file")
            return 3
        except InvalidURLError:
            cls.__print_error(
                "The public key URL in the file provided is invalid")
            return 4
        except PublicKeyNotExistsError:
            cls.__print_error(
                "The public key location contained in the file header either "
                "can't be accessed, or does not contain a public key",
            )
            return 5
        except InvalidSignature:
            cls.__print_error("There's something wrong with that file")
            return 6
        except DependencyMissingError as e:
            cls.__print_error(str(e))
            return 7
        except UnacceptableLocationError as e:
            cls.__print_error(str(e))
            return 8

        template = "\n  ✔  The file is verified as having originated at {}\n"
        cprint(template.format(domain), "green")

        return 0

    @staticmethod
    def __print_error(message):
        message = textwrap.fill(
            message, initial_indent="  ", subsequent_indent="  ", width=79)
        cprint("\n{}\n".format(message), "red")


if __name__ == "__main__":
    Command.run()
