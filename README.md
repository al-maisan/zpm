zpm
===

ZeroVM Package Manager


Packaging
---------

1. Install debian packaging dependencies:

    $ sudo apt-get install devscripts debhelper

2. Clone source from Git. Example:

    $ git clone https://github.com/zerovm/zpm.git $HOME/zpm

3. Amend the `debian/changelog` manually or using `dch` (preferred)

4. Create a gzipped tarball of the zpm source (minus the debian/ dir):

    $ tar czf ../zpm_0.1.orig.tar.gz * --exclude=debian

   Note that the .tar.gz file name will vary depending on the latest entry
   in the changelog.

5. Build a binary package:

    $ debuild

   or for a source package,

    $ debuild -S
