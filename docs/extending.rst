.. _extending:

Extending Aletheia
##################

Aletheia is the kind of project that works best if lots of people use it, so
any contribution you want to make toward making Aletheia more awesome is always
appreciated.

These are the top 3 categories that could use some attention, but even if you
just want to fix a typo in the documentation, send a pull request!


Packaging
=========

In a perfect world, Aletheia should be able to be installed without ``pip``,
but rather with your operating system's packaging manager.  One day, I'd like
to see an ``apt install aletheia``.  If you think that's something you could
help with, give it a shot and post to the issue queue if you have questions.

The priority package formats would be:

* Debian (apt)
* Redhat (yum)
* Gentoo (ebuild)
* Homebrew


Supporting Additional Formats
=============================

The library of supported formats is growing all the time, but if you have a
particular format in mind that you'd like to see working, Aletheia has been
designed to be very extendable.  Basically you've got three steps:

#. Create a file in the appropriate folder (either ``audio``, ``documents``,
   ``images``, or ``video``) and in it create a class that subclasses
   ``aletheia.file_types.base.File``.

#. At the very least, your class must define three methods:

   * ``.get_raw_data()``: This should return the "data" portion of the file
     (as opposed to the metadata).
   * ``.sign()``: While the actual signature generation and formatting of the
     metadata is done by the ``File`` class, the ``.sign()`` method needs to
     define *how* that metadata is written to your file type.
   * ``.verify()``: Like ``.sign()``, the hard part is done for you.  However
     you still need to define how we can retrieve the metadata from your file
     type.

#. Write some tests to cover your new file type.

If you're looking for a good place to start for an example, have a look at the
``HtmlFile``, ``Mp3File``, and ``JpegFile`` classes.  If you need help, just
post a question to the issue queue.


Porting to another language
===========================

As not everyone uses Python, it's probably a good idea to try to port Aletheia
to other languages.  For the most part, this is all just an elaborate wrapper
around FFmpeg, so porting shouldn't be all that difficult.  Priority languages
would include:

* Javascript
* Ruby
* Go
* Rust
* C#

If you like this project and would like to use it in another language, why not
give this a shot?
