pyletheia
=========

A Python implementation of `Aletheia`_.

.. _Aletheia: https://github.com/danielquinn/aletheia


Process
-------

The process is pretty simple:

1. Generate a public/private key pair
2. Sign an image with the private key
3. Publish your public key
4. Verify the image with your public key

System Requirements
-------------------

Aletheia makes us of the excellent Exiftool program which is available in most
Linux distributions:

Debian Linux and other derivatives like Ubuntu & Mint
.....................................................

.. code:: bash

    $ sudo apt install libimage-exiftool-perl

Arch Linux
..........

.. code:: bash

    $ sudo pacman -S perl-image-exiftool

Gentoo Linux
............

.. code:: bash

    $ sudo emerge exiftool


Installation
------------

As this is a Python package, use ``pip``:

.. code:: bash

    $ pip install aletheia


Command Line
------------

This package comes with a simple command-line program that does everything you
need to support the Aletheia process.


Generate your public/private key pair
.....................................

.. code:: bash

    $ aletheia generate
    Generating private/public key pair...

    All finished!

    You now have two files: aletheia.pem (your private key) and
    aletheia.pub (your public key).  Keep the former private, and share
    the latter far-and-wide.  Importantly, place your public key at a
    publicly accessible URL so that when you sign a file with your
    private key, it can be verified by reading the public key at that
    URL.

Your public & private key will be stored in ``${HOME}/.aletheia/``.  For
Aletheia to work, you need to publish your public key on a website somewhere so
it can be used to verify files later.


Sign an image with your private key
...................................

.. code:: bash

    $ aletheia sign file.jpg https://example.com/my-public-key.pub

Aletheia will modify the EXIF data on your image to include a signature and a
link to where your public key can be found so when it comes time to verify it,
everything that's necessary is available.


Verify the image with your public key
.....................................

.. code:: bash

    $ aletheia verify file.jpg

Now, anyone who receives your image can verify its origin with this command so
long as your public key remains available at the URL you used above.


Python API
----------

There's no reason that you would have to do all this on the command line of
course.  All of the above can be done programmatically as well.


Generate your public/private key pair
.....................................

.. code:: python

    from aletheia.utils import generate

    generate()

Just like the command line utility, ``generate()`` will create your
public/private key pair in ``${HOME}/aletheia``.


Sign an image with your private key
...................................

.. code:: python

    from aletheia.utils import sign

    my_image_file = "/path/to/file.jpg"
    public_key_location = "https://example.com/my-public-key.pub"

    sign(my_image_file, url)

So long as you've got your public/private key pair in ``${HOME}/aletheia/``,
``sign()`` will modify the metadata on your file to include a signature and
URL for your public key.

There is also a ``sign_bulk()`` utility for multiple files:

.. code:: python

    from aletheia.utils import sign

    my_image_files = ("/path/to/file1.jpg", "/path/to/file1.jpg")
    public_key_location = "https://example.com/my-public-key.pub"

    sign(my_image_files, url)


Verify the image with your public key
.....................................

.. code:: python

    from aletheia.utils import verify

    verify("/path/to/file.jpg")

Aletheia will import the public key from the URL in the file's metadata and
attempt to verify the image data by comparing the key to the embedded
signature.  If the file is verified, it returns ``True``, otherwise it returns
``False``.

There's also a ``verify_bulk()`` utility for multiple files:

.. code:: python

    from aletheia.utils import verify

    verify_bulk(("/path/to/file.jpg", "/path/to/file.jpg"))
