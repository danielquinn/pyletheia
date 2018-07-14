.. _commandline-api:

The Command Line API
####################

The command line interface operates with 3 different subcommands: ``generate``,
``sign``, and ``verify``, which generate keys, sign files, and verify files
respectively.


.. _commandline-api-generate:

Generating Keys
===============

If you're just planning on using Aletheia to verify the origin of a file, then
you don't need to generate keys.  This command is only for cases when you want
to sign a file with your private key and then share your public key with the
world.

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

* The path to the file you want to sign
* The URL for where you're storing your public key

.. code:: bash

    $ aletheia sign /path/to/file.jpg https://your-website.com/path/to/aletheia.pub

That URL is really important.  What we're doing here is writing some
instructions to your file that (a) claim authoriship of the file, and (b) tell
people where they can find the public key that proves that authorship.  This
means that if you sign and include a url, **your public key must always be
available at that URL** for verification to work.


Public Key URL in the Environment
---------------------------------

In cases where you might want to sign a lot of files and don't want to have to
specify the public key URL in every case (it's likely to be the same every time
after all), you can specify the key URL in your environment:

.. code:: bash

    $ export ALETHEIA_PUBLIC_KEY_URL=https://your-website.com/path/to/aletheia.pub
    $ aletheia sign /path/to/file.jpg
    $ aletheia sign /path/to/file.mkv
    $ aletheia sign /path/to/file.html


.. _commandline-api-verify:

Verification
============

Verification is easy, but note that it might require an internet connection as
Aletheia will attempt to fetch the public key (based on the URL in the signed
file) if it hasn't cached it already.  By now, you can probably guess what the
command looks like:

.. code:: bash

    $ aletheia verify /path/to/file.jpg
    $ aletheia verify /path/to/file.mkv
    $ aletheia verify /path/to/file.html

That's all there is to it.
