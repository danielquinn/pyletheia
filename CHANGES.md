## 0.2.0

* Dropped support for signing JpegImageFile objects.  The process was ugly and
  the overhead less-than-awesome.  Signing image files can still be done the
  standard way though: by operating on the file rather than the PIL object.
* More tests!

## 0.1.0

* Support for MP3 files
* You can now sign & verify images by either specifying a file name or passing
  in a `Pillow.JpegImageFile` instance.
* Location of the signature data in JPEG images was moved to
  `ImageIFD.HostComputer`.
* Dropped pyexiv2 and added mutagen & piexif as dependencies.

## 0.0.3

* A working implementation of Aletheia for JPEG images.
