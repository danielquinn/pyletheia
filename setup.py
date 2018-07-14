import os
import sys
from setuptools import setup

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# Shortcut for "publish" courtesy of the requests library
if sys.argv[-1] == "publish":
    os.system("rm -vr build dist")
    os.system("python setup.py build")
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    sys.exit()


setup()
