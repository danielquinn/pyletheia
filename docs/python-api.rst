.. _python-api:

The Python API
##############

The Python API is really just a lower-level of access to what's going on in the
command-line client.  The process however is the same: generate, sign, and
verify.

Handily, Aletheia has each of these common processes bundled into simple
functions that you can import from ``aletheia.utils``.


.. _python-api-generate:

Generating Keys
===============

To generate keys, simply import can call ``generate()``:

.. code-block:: python

    from aletheia.utils import generate

    generate()

Not much to see here.  The behaviour is identical to that of the ``generate``
command on the command line.  Similarly, the location of the generated keys can
be altered by setting ``ALETHEIA_HOME`` in your environment.  See
:ref:`commandline-api` for more details.


.. _python-api-sign:

Signing
=======

Like generating, signing is done with a single function.  The only difference
is that you must pass in two arguments:

* The path to the file you want to sign
* The URL for where you're storing your public key

Have a look at :ref:`commandline-api-sign` for an explanation as to the
importance of that second argument:

.. code-block:: python

    from aletheia.utils import sign

    sign("/path/to/file.jpg", "https://my-website.com/aletheia.pub")


Bulk Signing
------------

The process of setting up and tearing down Aletheia every time can be avoided
by using ``sign_bulk()``:

.. code-block:: python

    from aletheia.utils import sign_bulk

    sign_bulk(
        ("/path/to/file.jpg", "/path/to/file.mkv", "/path/to/file.html"),
        "https://my-website.com/aletheia.pub"
    )


.. _python-api-verify:

Verification
============

By now this should be looking familiar.  Verification is also handled by way of
a function:

.. code-block:: python

    from aletheia.utils import verify

    verify("/path/to/file.jpg")


This will attempt to fetch the URL stored in the file and then use that public
key to verify the file.  If you don't have an internet connection available,
and the public key hasn't already been cached, this process will fail.


Bulk Verification
-----------------

Just like signing, verification has a bulk helper function:

.. code-block:: python

    from aletheia.utils import verify

    verify_bulk(
        ("/path/to/file.jpg", "/path/to/file.mkv", "/path/to/file.html"),
    )


Optional Keyword Arguments
==========================

Each of the above commands will accept a series of keyword arguments that will
get passed up to the ``Aletheia`` class:

* ``private_key_path``: The path to the private key you want to generate or use
  to sign a file.
* ``public_key_path``: The path to where your public key should be generated
* ``cache_dir``: The path to the directory where you want Aletheia to store all
  the public keys it caches while verifying files.

Examples
--------

.. code-block:: python

    from aletheia.utils import generate, sign, verify

    generate(
        private_key_path="/path/to/private-key.pem",
        public_key_path="/path/to/public-key.pub",
    )
    sign(
        "/path/to/file.jpg",
        "https://my-website.com/aletheia.pub",
        private_key_path="/path/to/private-key.pem"
    )
    verify(
        "/path/to/file.jpg",
        cache_dir="/path/to/cache"
    )
