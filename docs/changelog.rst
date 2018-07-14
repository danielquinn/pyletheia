.. _changelog:

Changelog
#########

0.5.0
=====
* We now make use of ffmpeg's hashing features rather than trying to determine
  a "safe" way of drawing out the raw data from a file.
* Support for MKV files added.
* Support for Webm files added.
* The means of determining file type now includes support for guessing from
  file suffixes.

0.4.0
=====
* After some tinkering with a few alternatives, FFMpeg is now the standard way
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
