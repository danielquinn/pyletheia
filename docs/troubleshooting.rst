.. _troubleshooting:

Troubleshooting
###############

FFmpeg
======

With the exception of image processing, all of Aletheia's functions require a
working installation of `FFmpeg`_.  Thankfully, this program is Free software
and is available for all major platforms out there.  Installing it should be
relatively easy, but if Aletheia is complaining about how you don't have it
installed even after you're *sure* you did, note that FFmpeg must be installed
and available in your system ``PATH``.

.. _FFmpeg: https://ffmpeg.org/

This means that if you type ``ffmpeg -version`` on the command line, regardless
of what directory you're in, you should see something like this::

    built with gcc 8.1.1 (GCC) 20180531
    configuration: --prefix=/usr --disable-debug --disable-static --disable-stripping --enable-avresample --enable-fontconfig --enable-gmp --enable-gnutls --enable-gpl --enable-ladspa --enable-libaom --enable-libass --enable-libbluray --enable-libdrm --enable-libfreetype --enable-libfribidi --enable-libgsm --enable-libiec61883 --enable-libmodplug --enable-libmp3lame --enable-libopencore_amrnb --enable-libopencore_amrwb --enable-libopenjpeg --enable-libopus --enable-libpulse --enable-libsoxr --enable-libspeex --enable-libssh --enable-libtheora --enable-libv4l2 --enable-libvidstab --enable-libvorbis --enable-libvpx --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxcb --enable-libxml2 --enable-libxvid --enable-nvenc --enable-omx --enable-shared --enable-version3
    libavutil      56. 14.100 / 56. 14.100
    libavcodec     58. 18.100 / 58. 18.100
    libavformat    58. 12.100 / 58. 12.100
    libavdevice    58.  3.100 / 58.  3.100
    libavfilter     7. 16.100 /  7. 16.100
    libavresample   4.  0.  0 /  4.  0.  0
    libswscale      5.  1.100 /  5.  1.100
    libswresample   3.  1.100 /  3.  1.100
    libpostproc    55.  1.100 / 55.  1.100

If you see ``command not found`` or ``Bad command or file name``, then either
FFmpeg isn't installed, or it's not in your ``PATH``.  You'll have to talk to
someone who knows more about your operating system than I do to figure out how
to get that to work.
