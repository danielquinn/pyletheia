.. _commandline-api:

The Command Line API
####################

The command line interface supports 5 different subcommands: ``generate``,
``sign``, and ``verify``, which generate keys, sign files, and verify files
respectively, and ``public-key`` and ``private-key`` which simply print out the
relevant key for you to make use of it.


.. _commandline-api-generate:

Generating Keys
===============

If you're just planning on using Aletheia to verify the origin of a file, then
you don't need to generate keys.  This command is only for cases when you want
to sign a file.

Generation is easy though, as Aletheia takes the complication out of the
process.  All you have to do is:

.. code:: bash

    $ aletheia generate

That's it.  After a few moments, Aletheia will generate new public and private
keys and store them in ``${HOME}/.config/aletheia/`` by default.  The private
and public keys will be named ``aletheia.pem`` and ``aletheia.pub``
respectively.


Changing the Default Home Directory
-----------------------------------

By default, Aletheia assumes that you want all of your Aletheia-related files
stuffed into ``${HOME}/.config/aletheia/``, but you can change that if you like
by setting ``ALETHEIA_HOME`` in your environment:

.. code:: bash

    $ ALETHEIA_HOME="/path/to/somewhere/else" aletheia generate


.. _commandline-api-sign:

Signing
=======

Once you have some keys generated, you can use them to sign files with the
``sign`` subcommand.  Importantly signing requires two things:

* The path to the file you want to sign.
* The domain to which you're attributing the origin of the file.

.. code:: bash

    $ aletheia sign /path/to/file.jpg example.com

What we're doing here is writing some instructions to your file that (a) claim
authoriship of the file, and (b) tell people where they can find the public key
that proves that authorship.  This means that **your public key must always be
available at that domain** (either via DNS or at
``https://example.com/aletheia.pub``) for verification to work.


Domain in the Environment
-------------------------

In cases where you might want to sign a lot of files and don't want to have to
specify the domain name in every case (it's likely to be the same every time
after all), you can specify the domain in your environment:

.. code:: bash

    $ export ALETHEIA_DOMAIN=example.com
    $ aletheia sign /path/to/file.jpg
    $ aletheia sign /path/to/file.mkv
    $ aletheia sign /path/to/file.html


.. _commandline-api-verify:

Verification
============

Verification is easy, but note that it might require an internet connection as
Aletheia will attempt to fetch the public key (based on the domain in the
signed file) if it hasn't cached it already.  By now, you can probably guess
what the command looks like:

.. code:: bash

    $ aletheia verify /path/to/file.jpg
    $ aletheia verify /path/to/file.mkv
    $ aletheia verify /path/to/file.html

That's all there is to it.


Getting Your Public & Private Keys
==================================

Aletheia provides a handy interface for reading your public & private keys so
you can copy/paste the text somewhere useful.

Your Private Key
----------------

You can get your private key with the ``private-key`` subcommand:

.. code:: bash

    $ aletheia private key
    -----BEGIN RSA PRIVATE KEY-----
    MIISKQIBAAKCBAEA0qKTDRq/sPsLLZ+C+kr2eONfKYUZFYYNJ+if2oMKqj8pXr4s
    J6qG8Z3FBMlcvx9gmKslByUv68DbGVrH/zBdEU+/XOI3cCqn1+Pblz0r2UDgl97z
    7xThq3y6CA1NvI36kcipuzA1HOTMXVdb4voG095CbRo96K+eLXtLpYSvAkzZTCCa
    O2UZTcAdb0Nc+BUB3c9GWioLSXADgJKjaqZGMGEGuOKEsHovXc3t+9yNm4Q4YlBl
    ...

Your Public Key
---------------

Your public key can be recognised in either ``PKCS1`` format or ``OpenSSH``
format.  Handily, you can use the ``public-key`` subcommand to get your key in
either format.

To see the default ``PKCS1`` format, you can call ``public-key`` without any
options, or with ``--format pkcs1``:

.. code:: bash

    $ aletheia public-key
    -----BEGIN RSA PUBLIC KEY-----
    MIIECgKCBAEA0qKTDRq/sPsLLZ+C+kr2eONfKYUZFYYNJ+if2oMKqj8pXr4sJ6qG
    8Z3FBMlcvx9gmKslByUv68DbGVrH/zBdEU+/XOI3cCqn1+Pblz0r2UDgl97z7xTh
    q3y6CA1NvI36kcipuzA1HOTMXVdb4voG095CbRo96K+eLXtLpYSvAkzZTCCaO2UZ

For OpenSSH format, use ``--format openssh``:

.. code:: bash

    $ aletheia public-key --format openssh
    ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAEAQDSopMNGr+w+wstn4L6SvZ4418phRkVhg...
