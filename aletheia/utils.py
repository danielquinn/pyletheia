from .aletheia import Aletheia


def generate():
    Aletheia.generate()


def sign(path, public_key_url):
    Aletheia().sign(path, public_key_url)


def sign_bulk(paths, public_key_url):
    aletheia = Aletheia()
    for path in paths:
        aletheia.sign(path, public_key_url)


def verify(path):
    Aletheia().verify(path)


def verify_bulk(paths):
    aletheia = Aletheia()
    for path in paths:
        aletheia.verify(path)
