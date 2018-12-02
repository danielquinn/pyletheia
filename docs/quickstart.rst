.. _quickstart:

QuickStart
==========

Getting up & running with Aletheia doesn't take long at all the process is
simple:

1. Check out :ref:`setup` to install Aletheia on your system.
2. Use the ``aletheia`` command to generate your public and private keys.  Have
   a look at :ref:`commandline-api` for details on that.
3. Put your public key on the web (details below)
4. Sign your files using the ``aletheia`` command.

If you only want to use Aletheia to verify stuff you find online, you don't
event need to worry about steps 2-4.


A Little More Information
-------------------------

Let's go over steps 2-4 a little closer as step 1 is pretty well covered in
:ref:`setup`.


Generating Your Keys
~~~~~~~~~~~~~~~~~~~~

Aletheia allows you to attach your authorship to a file through a process
called *public key cryptography*.  The process is pretty simple:

1. You use Aletheia to create two files: a *private key* and a *public key*.
    * You keep your private key safe and don't share it with anyone.
    * You put your public key on your webserver where Aletheia knows to look for it.
2. You use Aletheia to *"sign"* your files.  This tags them in such a way that
   other people can then use Aletheia to verify the file came from you.

Key generation is a one-step process.  Just open a shell and type this:

.. code:: bash

    $ aletheia generate

That'll take a few moments.  When you're done, you have to decide where you
want to store your public key.  You have two options:

1. In your DNS configuration as a ``TXT`` record.
2. On your webserver at ``/aletheia.pub``.

You only need to do *one* of these, but it doesn't hurt to do both.


Storing Your Key in DNS
.......................

As DNS TXT records don't much line line breaks, you should store your key in
OpenSSH format.  So, the first step is to get your public key in said format:


.. code:: bash

    $ aletheia public-key --format=openssh

Copy & paste the output of this command into a TXT record for your domain,
prefixing it with `aletheia-public-key=`.  The result should look something
like this:

    example.com.	3599	IN	TXT	"aletheia-public-key=ssh-rsa AAAAB3NzaC1yc2E...

Note that there's an RFC that requires that TXT records not exceed a length of
255 characters, but the work-around is to store the single key as a series of
strings on the same record.  If you're curious about what this looks like, make
sure you've got ``dig`` installed and have a look at ``danielquinn.org``:

.. code:: bash

    $ dig danielquinn.org txt


Storing Your Key on Your Webserver
..................................

As an alternative to DNS, you can also just host your public key on your
webserver so long as:

1. The file is accessible at ``/aletheia.pub``
2. Your site supports SSL

Just get a copy of your public key:

.. code:: bash

    $ aletheia public-key

And put the output of that command into a file called ``aletheia.pub``.
Finally, upload that file to your website.  You'll know you've got it right if
you can go to ``https://yourwebsite.com/aletheia.pub`` and the result is your
public key.


Signing Your File(s)
~~~~~~~~~~~~~~~~~~~~

Finally, you've got your public key where other people running Aletheia can
find it, so now it's time to sign your files.  Have a look at
:ref:`commandline-api` again for more info, but here's the quick version:

.. code:: bash

    $ aletheia sign /path/to/my/file.jpg my-website.com
