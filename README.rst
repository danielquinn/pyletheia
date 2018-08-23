pyletheia
=========
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
