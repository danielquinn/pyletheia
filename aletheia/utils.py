#
# Python API:
#
#   from aletheia import generate, sign, verify
#
#   generate()
#
#   sign(path, domain)
#   sign_bulk(paths, domain)
#
#   verify(path)
#   verify_bulk(paths)
#

from multiprocessing import Pool, cpu_count

from .aletheia import Aletheia


def generate(**kwargs):  # pragma: nocov
    """
    Creates your public/private key pair and either stores them in
    ``${ALETHEIA_HOME}/.aletheia/``, or if you provide ``public_key_path`` and
    ``private_key_path``, it'll store them there.  All keyword arguments are
    passed to the Aletheia constructor.
    """
    Aletheia(**kwargs).generate()


def sign(path, domain, **kwargs):  # pragma: nocov
    """
    Attempts to sign an file with your private key.  If you provide a
    ``private_key_path``, Aletheia will look for it there, otherwise it will
    look for it in the environment under ``ALETHEIA_PRIVATE_KEY``, and failing
    that, assume ``${ALETHEIA_HOME}/.aletheia/aletheia.pem``.
    """
    Aletheia(**kwargs).sign(path, domain)


def sign_bulk(paths, domain, **kwargs):
    """
    Does what ``sign()`` does, but for lots of files, saving you the setup &
    teardown time for key handling and parallelising it across all available
    cores.
    """

    total_paths = len(paths)
    per_thread = total_paths // cpu_count()
    groups = [paths[_:_+per_thread] for _ in range(0, total_paths, per_thread)]

    with Pool() as pool:
        pool.map(__sign_files, [(_, kwargs, domain) for _ in groups])


def verify(path, **kwargs):  # pragma: nocov
    """
    Aletheia will import the public key from the URL in the file's metadata and
    attempt to verify the data by comparing the key to the embedded signature.
    If the file is verified, it returns ``True``, otherwise it returns
    ``False``.  Aside from the ``path``, all keyword arguments are passed to
    the Aletheia constructor.
    """
    return Aletheia(**kwargs).verify(path)


def verify_bulk(paths, **kwargs):
    """
    Does what ``verify()`` does, but for lots of files, saving you the setup &
    teardown time for key handling and parallelising it across all available
    cores.
    """

    total_paths = len(paths)
    per_thread = total_paths // cpu_count()
    groups = [paths[_:_+per_thread] for _ in range(0, total_paths, per_thread)]

    with Pool() as pool:
        r = pool.map(__verify_files, [(_, kwargs) for _ in groups])

    return {k: v for d in r for k, v in d.items()}


def __sign_files(args):

    paths, kwargs, domain = args

    aletheia = Aletheia(**kwargs)

    for path in paths:
        aletheia.sign(path, domain)


def __verify_files(args):

    paths, kwargs = args

    aletheia = Aletheia(**kwargs)

    results = {}
    for path in paths:
        results[path] = aletheia.verify(path)

    return results
