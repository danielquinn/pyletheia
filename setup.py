import os
from os.path import abspath, dirname, join
from setuptools import setup

__version__ = ()
with open("aletheia/version.py") as f:
    exec(f.read())

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# Get proper long description for package
current_dir = dirname(abspath(__file__))

with open(join(current_dir, "README.rst")) as f:
    description = f.read()

# Get the long description from README.md
setup(
    name="aletheia",
    version=".".join([str(_) for _ in __version__]),
    packages=["aletheia"],
    include_package_data=True,
    license="AGPLv3",
    description="A Python implementation of Aletheia",
    long_description=description,
    url="https://github.com/danielquinn/pyletheia",
    download_url="https://github.com/danielquinn/pyletheia",
    author="Daniel Quinn",
    author_email="code@danielquinn.org",
    maintainer="Daniel Quinn",
    maintainer_email="code@danielquinn.org",
    install_requires=[
        "cryptography==2.1.2",
        "requests==2.18.4",
    ],
    tests_require=[
    ],
    extras_require={
        "doc": ["sphinx", "sphinx_rtd_theme"],
    },
    test_suite="pytest",
    scripts=[
        "scripts/aletheia",
    ],
    keywords=["Command Line", "verification", "fake news"],
    classifiers=[
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
