Aletheia for Python
===================
|PyPi| |Thanks!| |License| |Documentation|

A Python 3 implementation of `Aletheia`_.

.. _Aletheia: https://github.com/danielquinn/aletheia
.. |PyPi| image:: https://img.shields.io/pypi/pyversions/aletheia.svg
   :target: https://pypi.org/project/aletheia/
.. |Thanks!| image:: https://img.shields.io/badge/THANKS-md-ff69b4.svg
   :target: https://github.com/danielquinn/pyletheia/blob/master/THANKS.md
.. |License| image:: https://img.shields.io/github/license/danielquinn/pyletheia.svg
   :target: https://github.com/danielquinn/pyletheia/blob/master/LICENSE
.. |Documentation| image:: https://readthedocs.org/projects/aletheia-project/badge/?version=latest
   :target: https://aletheia-project.readthedocs.io/en/latest/

This is how we get from

    I read it on the Internet, so it must be true.

to

    Yesterday, the Guardian had a story about a prominent politician doing
    something they weren't supposed to be doing.  The video footage was
    certified authentic, and the author of the article stands by her work.

Aletheia is a little program you run to attach your name -- and reputation --
to the files you create: audio, video, and documentation, all of it can carry
authorship, guaranteed to be tamper proof.

Once you use Aletheia to sign your files, you can share them all over the web,
and all someone has to do to verify the file's author is run Aletheia against
the file they just received.  The complication of fetching public keys and
verifying signatures is all done for you.

If this sounds interesting to you, have a look at `the documentation`_ or even
install it and try it out yourself.

.. _the documentation: https://aletheia-project.readthedocs.io/en/latest/


The Goal
--------

I want to live in a world where journalism means something again.  Where "some
guy on the internet" making unsubstantiated claims can be fact-checked by
organisations who have a reputation for doing the work of accurate reporting.
More importantly though, I think we need a way to be able to trust what we see
again.

New technologies are evolving every day that allow better and better fakes to
be created.  Now more than ever we need a way to figure out whether we trust
the source of something we're seeing.  This is an attempt to do that.


How to Use it
-------------

The process is pretty straight forward.  Install the system dependencies as
described in the `setup documentation`_ and then:

.. code-block:: bash

    $ pip install aletheia

Once it's installed, you can verify a file to try it out.  Use `this one`_ as a
starting example.


Command Line API
................

.. code-block:: bash

    $ aletheia verify path/to/test.jpg


Python API
..........

.. code-block:: python

    from aletheia.utils import verify

    verify("path/to/test.jpg")


More details can be found in the `command line API`_ and `Python API`_ documentation.

.. _this one: https://danielquinn.org/media/cache/thumbnails/gallery/2014/11/3/139743.jpg.800x534_q85_crop-smart.jpg
.. _setup documentation: https://aletheia-project.readthedocs.io/en/latest/setup.html
.. _command line API: https://aletheia-project.readthedocs.io/en/latest/commandline-api.html
.. _Python API: https://aletheia-project.readthedocs.io/en/latest/python-api.html


Colophon & Disambiguation
-------------------------

This project is named for the Greek goddess of truth & verity -- a reasonable
name for a project that's trying to restore truth and verified origins to the
web.  It also doesn't hurt that the lead developer's wife is Greek ;-)

It's been noted that there's `another project out there with the same name`_.
The two projects are totally unrelated, despite the identical name *and* the
fact that both lead developers are named "Daniel".

.. _another project out there with the same name: https://github.com/daniellerch/aletheia
