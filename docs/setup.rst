.. _setup:

Setup
#####

Aletheia is a reasonably simple program that stands on top of a few well-known
software packages out there.  In order to use it, you'll need to install the
requirements first, and then install Aletheia with the Python package manager.


.. _setup-requirements:

Requirements
============

System Dependencies
-------------------

Aletheia requires ``libmagic``, which comes standard with most Linux & BSD
systems, but may need to be installed on your system if you're running OSX or
Windows.  For OSX, you can install this with Homebrew with
``brew install libmagic``, but I'm not sure what happens with Windows.

In addition to libmagic, Aletheia needs to have the ability to talk to two
external programs:

* `FFmpeg`_: used to read & write audio & video files.
* `exiftool`_: used to read & write image files.

Installing both of these is easy on any platform though, even Windows ;-)

The download & installation instructions for your operating system of choice
can be found on their respective project pages.  Once that's finished, and you
can successfully execute ``ffmpeg`` and ``exiftool`` on the command line,
you're ready to install Aletheia.

.. _FFmpeg: https://ffmpeg.org/
.. _exiftool: https://sno.phy.queensu.ca/~phil/exiftool/


Python
------

Aletheia was written for modern versions of Python, so you'll need Python 3.5
or higher to get things running.  If you're stuck using a system without a
modern version available, `the pyenv project`_ provides a handy means of
getting modern python on any system that can run Bash.

.. _the pyenv project: https://github.com/pyenv/pyenv


.. _setup-installation:


Installation
============

As Aletheia is just a Python package, installing it is easy with pip:

.. code:: bash

    $ pip install aletheia

This will download the package and install it for you.  Along with the Python
library (so you can ``import aletheia``), you also get the command line
program, which you can call like this:

.. code:: bash

    $ aletheia generate
    $ aletheia sign /path/to/file.jpg example.com
    $ aletheia verify /path/to/file.jpg

See :ref:`commandline-api` for more information about how to use Aletheia on
the command line, and the :ref:`python-api` for how to use it in your own
scripts.
