.. _changelog:

Changelog
#########

2.0.0
=====

Considerable changes have been made to the way we connect a file to a domain.
While v1.x assigned ownership of a file to a domain based on the existence
of a public key *anywhere* on that domain, v2.x now introduces further
restrictions on where that key must be hosted.  This is to prevent hosting
providers from being implicated by people who have the ability to host files
on their platform.

The new rules are a lot simpler though.  You can host your public key in
only one of two places:

1. On your web server at ``https://your-domain.com/aletheia.pub``
2. In a DNS TXT record for your domain.  In this case, your public key should
   be stored in OpenSSH format so it all fits on one line.  Have a look at
   [the DNS record for danielquinn.org](https://www.digwebinterface.com/?hostnames=danielquinn.org&type=TXT&ns=resolver&useresolver=8.8.4.4&nameservers=)
   if you want an example of what this looks like.

A few other features were added as well:

* You can now call ``aletheia public-key`` to display your public key.
  Similarly, you can call ``aletheia public-key --format=openssh`` for the
  aforementioned OpenSSH formatting required for DNS storage.
* You can also call ``aletheia private-key`` to display your private key.


1.1.0
=====

* Added support for Markdown files.


1.0.1
=====

* Added a ``--version`` flag to the command line interface.
* Added some performance tweaks to how we're calling exiftool.
* Updated various exceptions to include a little more information about what
  went wrong.  `#4`_

.. _#4: https://github.com/danielquinn/pyletheia/issues/4


1.0.0
=====

* Use of Pillow and piexif have been dropped in favour of `exiftool`_.  This
  was due largely to the fact that Pillow's ``.tobytes()`` method performs
  differently from environment to environment, making Aletheia's job quite
  impossible.  Standardising on exiftool means reproducible results regardless
  of what operating system you're using.  Unfortunately, this also means that
  files signed with past versions of Aletheia will fail a verification check in
  this new version.
* GIF and PNG files are now supported, thanks to the inclusion of exiftool.
* The tests were restructured to handle a multi-threaded test environment
  better.  You can now run the tests with ``pytest -n auto`` on multi-cored
  machines for a significant speed improvement.

.. _exiftool: https://sno.phy.queensu.ca/~phil/exiftool/


0.6.4
=====

* Bugfix release: Attempting to run Aletheia on a video file will now no longer
  explode with a traceback if FFMpeg isn't installed.


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
