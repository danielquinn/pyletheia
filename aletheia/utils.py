#
# Python API:
#
#   from aletheia import generate, sign, verify
#
#   generate()
#
#   sign(path, public_key_url)
#   sign_bulk(paths, public_key_url)
#
#   verify(path)
#   verify_bulk(paths)
#

from .aletheia import Aletheia


def generate(**kwargs):
    """
    Creates your public/private key pair and either stores them in
    ``${ALETHEIA_HOME}/.aletheia/``, or if you provide ``public_key_path`` and
    ``private_key_path``, it'll store them there.  All keyword arguments are
    passed to the Aletheia constructor.
    """
    Aletheia(**kwargs).generate()


def sign(path, public_key_url, **kwargs):
    """
    Attempts to sign an image with your private key.  If you provide a
    ``private_key_path``, Aletheia will look for it there, otherwise it will
    assume ``${ALETHEIA_HOME}/.aletheia/``
    """
    Aletheia(**kwargs).sign(path, public_key_url)


def sign_bulk(paths, public_key_url, **kwargs):
    """
    Does what ``sign()`` does, but for lots of files, saving you the setup &
    teardown time for key handling.
    """
    aletheia = Aletheia(**kwargs)
    for path in paths:
        aletheia.sign(path, public_key_url)


def verify(path, **kwargs):
    """
    Aletheia will import the public key from the URL in the file's metadata and
    attempt to verify the image data by comparing the key to the embedded
    signature.  If the file is verified, it returns ``True``, otherwise it
    returns ``False``.  Aside from the ``path``, all keyword arguments are
    passed to the Aletheia constructor.
    """
    return Aletheia(**kwargs).verify(path)


def verify_bulk(paths, **kwargs):
    """
    Does what ``verify()`` does, but for lots of files, saving you the setup &
    teardown time for key handling.
    """
    aletheia = Aletheia(**kwargs)
    results = {}
    for path in paths:
        results[path] = aletheia.verify(path)
    return results
