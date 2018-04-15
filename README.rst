pyletheia
=========

A Python implementation of `Aletheia`_.

.. _Aletheia: https://github.com/danielquinn/aletheia


Process
-------

The process is pretty simple:

1. Generate a public/private key pair
2. Sign a media file (image, audio, video) with the private key
3. Publish your public key
4. People can now verify your media files with your public key


Installation
------------

As this is a Python package, use ``pip``:

.. code:: bash

    $ pip install aletheia

Configuration
-------------

Aletheia puts all of the required key files and cached public keys into
``${ALETHEIA_HOME}`` which by default is ``${HOME}/.config/aletheia``.  You
can override this by setting it in the environment.


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

Your public & private key will be stored in ``${ALETHEIA_HOME}``. For Aletheia
to work, you need to publish your public key on a website somewhere so it can
be used to verify files later.


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
public/private key pair in ``${ALETHEIA_HOME}``.


Sign an image with your private key
...................................

.. code:: python

    from aletheia.utils import sign

    sign("/path/to/file.jpg", "https://example.com/my-public-key.pub")

So long as you've got your public/private key pair in ``${ALETHEIA_HOME}``,
``sign()`` will modify the metadata on your file to include a signature and URL
for your public key.

There is also a ``sign_bulk()`` utility for multiple files:

.. code:: python

    from aletheia.utils import sign

    sign(
        ("/path/to/file1.jpg", "/path/to/file2.jpg"),
        "https://example.com/my-public-key.pub"
    )


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

    verify_bulk(("/path/to/file1.jpg", "/path/to/file2.jpg"))
