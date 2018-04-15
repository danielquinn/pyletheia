## 0.1.0

* Support for MP3 files
* You can now sign & verify images by either specifying a file name or passing
  in a `Pillow.JpegImageFile` instance.
* Location of the signature data in JPEG images was moved to
  `ImageIFD.HostComputer`.
* Dropped pyexiv2 and added mutagen & piexif as dependencies.

## 0.0.3

* A working implementation of Aletheia for JPEG images.
