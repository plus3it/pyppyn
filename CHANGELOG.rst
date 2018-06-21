CHANGE LOG
==========

0.3.4 - 2018.06.20
------------------
* [BUG FIX] Determining available module(s) from a package
  was not working on Windows. This functionality is not
  required by GravityBee so it was removed to allow
  everything to work smoothly on Windows.
* [ENHANCEMENT] Cleaned up code, comments.

0.3.3 - 2018.05.07
------------------
* [ENHANCEMENT] Integrate with `Satsuki <https://github.com/YakDriver/satsuki>`_ to simplify the release process.
* [ENHANCEMENT] Integrate with `GravityBee <https://github.com/YakDriver/gravitybee>`_ to create standalone
  executables for platforms.

0.3.2 - 2018.04.26
------------------
* [BUG FIX] Minor tweak to way that work directories are created to
  avoid namespace collisions using UUIDs.

0.3.1 - 2018.04.24
------------------
* [ENHANCEMENT] Add convenience methods for accessing configuration data.
* [BUG FIX] Improve state handling.

0.3.0 - 2018.04.23
------------------
* [ENHANCEMENT] Now provides support for packages with setup.py
  and/or setup.cfg configuations.

0.2.3 - 2018.04.16
------------------
* [ENHANCEMENT] Improved usability by maintaining state of instances
  of ConfigRep, so methods can be called and object will know whether
  it is in the correct state to respond. It will call appropriate
  prerequisite methods if not.
* [ENHANCEMENT] Provide a convenience method to give all required
  packages in one list.

0.2.2 - 2018.04.13
------------------
* [ENHANCEMENT] Changed format of readme and changelog to RST, and
  simplified setup.py as a result.

0.2.1 - 2018.04.13
------------------
Provides these capabilities (in limited form):

* [ENHANCEMENT] Extract package dependencies from setup.cfg file.
* [ENHANCEMENT] Determine which dependencies will be needed on the
  current os/python version.
* [ENHANCEMENT] Find a module associated with a package.
* [ENHANCEMENT] Install (and import) dependencies.

0.1.0 - 2018.04.10
------------------
* Initial release!
