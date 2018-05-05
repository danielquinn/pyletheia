import os
import sys
from os.path import abspath, dirname, join
from setuptools import setup

from aletheia import __version__

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# Shortcut for "publish" courtesy of the requests library
if sys.argv[-1] == "publish":
    os.system("rm -vr build dist")
    os.system("python setup.py build")
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    sys.exit()


# Get proper long description for package
with open(join(dirname(abspath(__file__)), "README.rst")) as f:
    description = f.read()

# Get the long description from README.md
setup(
    name="aletheia",
    version=".".join([str(_) for _ in __version__]),
    packages=[
        "aletheia",
        "aletheia.file_types"
    ],
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
        "Pillow>=5.0.0",
        "cryptography>=2.1.3",
        "mutagen>=1.40.0",
        "piexif>=1.0.13",
        "python-magic>=0.4.15",
        "requests>=2.18.4",
        "six",
        "termcolor>=1.1.0",
    ],
    tests_require=[
        "pytest",
        "pytest-sugar"
    ],
    extras_require={
        "doc": ["sphinx", "sphinx_rtd_theme"],
    },
    test_suite="pytest",
    entry_points={
        "console_scripts": [
            "aletheia=aletheia.cli:Command.run"
        ]
    },
    keywords=["Command Line", "verification", "fake news"],
    classifiers=[
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
