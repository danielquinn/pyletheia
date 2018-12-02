# Test Data

The files in this directory are used for running the tests.  Don't try to use
the public & private keys here, eh? 🍁


## An explanation regarding the naming convention:

### Keys

* `keys/private.pem`: A private key, used exclusivly for testing
* `keys/public.pkcs1`: The associated public key in PKCS1 format
* `keys/public.openssh`: The same public key in OpenSSH format

### Media Files

* `original/test.<extension>`: A plain file, untouched by Aletheia
* `signed/test.<extension>`: A copy of the original, successfully signed.
* `bad/test.<extension>`: A copy of the original, signed with a signature that
  looks like it could be legit, but isn't.
* `broken/test.<extension>`: A copy of the original, with malformed data in the
  signature.
* `future/test.<extension>`: A signed copy of the original, with the schema
  version set into the future.


## Attributions

* Webm, MP4, and OGV files are courtesy of [TechSlides](http://techslides.com/sample-webm-ogg-and-mp4-video-files-for-html5)
