.. _setup:

Setup
#####

Aletheia is a reasonably simple program that stands on top of a few well-known
software packages out there.  In order to use it, you'll need to install the
requirements first, and then install Aletheia with the Python package manager.


.. _setup-requirements:

Requirements
------------

Outside of the Python magic going on under the hood, Aletheia needs to have
the ability to talk to the exceptional `FFmpeg`_ program as well.  Installing
it is easy on any platform though, even Windows ;-)

The download & installation instructions for your operating system of choice
can be found `on the project page`_.  Once that's finished, and you can
successfully execute ``ffmpeg`` on the command line, you're ready to install
Aletheia.

.. _FFmpeg: https://ffmpeg.org/
.. _on the project page: http://ffmpeg.org/download.html


.. _setup-installation:


Installation
------------

As Aletheia is just a Python package, installing it is easy with pip:

.. code:: bash

    $ pip install aletheia

This will download the package and install it for you.  Along with the Python
library (so you can ``import aletheia``), you also get the command line
program, which you can call like this:

.. code:: bash

    $ aletheia generate
    $ aletheia sign /path/to/file.jpg https://example.com/aletheia.pub
    $ aletheia verify /path/to/file.jpg

See :ref:`commandline-api` for more information about how to use Aletheia on
the command line, and the :ref:`python-api` for how to use it in your own
scripts.
