.. _changelog:

Changelog
#########

0.6.3
=====
* Changed the dependency on file-magic to require a minimum of v0.3.0 rather
  than v0.4.0.  This is to make packaging for Arch Linux easier.
* Added a new function to ``setup.py`` to automatically generate a PKGBUILD
  file.
* Removed ``scripts/*`` from the ``MANIFEST`` file as that directory is no
  longer used.

0.6.2
=====

* Added support for Python 3.5.  Aletheia now supports CPython 3.5, 3.6, 3.7,
  and PyPy 3.5 v6.0.0


0.6.1
=====

* Switched to using `file-magic`_ instead of `python-magic`_.  The effects &
  performance are the same, but file-magic appears to be more commonly used in
  different Linux distros and I'd like for packaging to be as easy as possible.
* Added tox tests for Python 3.7

.. _file-magic: https://pypi.org/project/file-magic/
.. _python-magic: https://pypi.org/project/python-magic/


0.6.0
=====

* We now make use of FFmpeg's hashing features rather than trying to determine
  a "safe" way of drawing out the raw data from a file.
* Support for MKV files added.
* Support for Webm files added.
* The means of determining file type now includes support for guessing from
  file suffixes.


0.5.0
=====

* Support for HTML files added.


0.4.0
=====

* After some tinkering with a few alternatives, FFmpeg is now the standard way
  to generate the "raw data" component for audio & video.
* Support for MP4 files added.


0.3.4
=====

* Fix a bug in environment variable referencing for public key URL.


0.3.3
=====

* Error out gracefully if we attempt to verify a file that doesn't contain a
  signature.


0.3.2
=====

* Prettied up the CLI output with a few emojis and colours.


0.3.1
=====

* Add tox to help get us to a point where Python 2.7 is supported
* Fix a bug in the shebang in the CLI script and modify setup.py to use
  ``entry_points=`` instead of ``scripts=`` as the latter method had a tendency
  to overwrite the shebang line in the ``aletheia`` script.
* Lastly, we now have Even More Tests.


0.3.0
=====

* Added colours to the output of the command-line script.  This means a new
  dependency on the ``termcolor`` library.
* **Breaking**: ``verify()`` now raises various exceptions on failure rather
  than simply returning ``False``.  This was done to allow the command-line
  script to show useful error messages.
* The command-line script is a lot more helpful now in terms of error
  messages.


0.2.0
=====

* Dropped support for signing JpegImageFile objects.  The process was ugly and
  the overhead less-than-awesome.  Signing image files can still be done the
  standard way though: by operating on the file rather than the PIL object.
* More tests!


0.1.0
=====

* Support for MP3 files
* You can now sign & verify images by either specifying a file name or passing
  in a ``Pillow.JpegImageFile`` instance.
* Location of the signature data in JPEG images was moved to
  ``ImageIFD.HostComputer``.
* Dropped pyexiv2 and added mutagen & piexif as dependencies.


0.0.3
=====

* A working implementation of Aletheia for JPEG images.
