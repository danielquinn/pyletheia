from .aletheia import Aletheia


def generate():
    """
    Creates your public/private key pair and stores it in ``${HOME}/aletheia``.
    """
    Aletheia.generate()


def sign(path, public_key_url):
    """
    So long as you've got your public/private key pair in
    ``${HOME}/aletheia/``, ``sign()`` will modify the metadata on your file to
    include a signature and URL for your public key.
    """
    Aletheia().sign(path, public_key_url)


def sign_bulk(paths, public_key_url):
    """
    Does what ``sign()`` does, but for lots of files, saving you the setup &
    teardown time for key handling.
    """
    aletheia = Aletheia()
    for path in paths:
        aletheia.sign(path, public_key_url)


def verify(path):
    """
    Aletheia will import the public key from the URL in the file's metadata and
    attempt to verify the image data by comparing the key to the embedded
    signature.  If the file is verified, it returns ``True``, otherwise it
    returns ``False``.
    """
    return Aletheia().verify(path)


def verify_bulk(paths):
    """
    Does what ``verify()`` does, but for lots of files, saving you the setup &
    teardown time for key handling.
    """
    aletheia = Aletheia()
    results = {}
    for path in paths:
        results[path] = aletheia.verify(path)
    return results
