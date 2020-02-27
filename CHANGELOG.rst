CHANGE LOG
==========

0.3.17 - 2020.02.27
-------------------
* [FIX] Remove standard packages from setup.cfg install requires.

0.3.13 - 2020.01.15
-------------------
* [ENHANCEMENT] Remove pipenv files, update setup.cfg dependencies.

0.3.12 - 2020.01.14
-------------------
* [ENHANCEMENT] Update dependencies.

0.3.11 - 2019.05.06
-------------------
* [ENHANCEMENT] Update dependencies.

0.3.10 - 2019.02.05
-------------------
* [ENHANCEMENT] Perform work in '.pyppyn' directory.

0.3.9 - 2019.01.29
------------------
* [ENHANCEMENT] Minor cleanup.
* [ENHANCEMENT] Transfer to Plus3IT.

0.3.8 - 2019.01.24
------------------
* [ENHANCEMENT] Restructure Travis CI linting, testing, deploying so
  deploy only happens when other stages complete successfully.
* [ENHANCEMENT] Improve speed of MacOS builds significantly.

0.3.7 - 2019.01.23
------------------
* [ENHANCEMENT] Minor change to Travis CI, remove AppVeyor.

0.3.6 - 2019.01.23
------------------
* [ENHANCEMENT] Replace print with log.
* [ENHANCEMENT] Improve compatibility across Windows, MacOS,
  Linux; add tests to Travis CI.

0.3.5 - 2019.01.05
------------------
* [ENHANCEMENT] Fix flake8, pylint issues, add pipenv Pipfile, fix
  compatibility with Python 3.7.

0.3.4 - 2018.06.20
------------------
* [FIX] Determine available module(s) from a package
  was not working on Windows. This functionality is not
  required by GravityBee so it was removed to allow
  everything to work smoothly on Windows.
* [ENHANCEMENT] Clean up code, comments.

0.3.3 - 2018.05.07
------------------
* [ENHANCEMENT] Integrate with `Satsuki <https://github.com/plus3it/satsuki>`_ to simplify the release process.
* [ENHANCEMENT] Integrate with `GravityBee <https://github.com/plus3it/gravitybee>`_ to create standalone
  executables for platforms.

0.3.2 - 2018.04.26
------------------
* [FIX] Minor tweak to way that work directories are created to
  avoid namespace collisions using UUIDs.

0.3.1 - 2018.04.24
------------------
* [ENHANCEMENT] Add convenience methods for accessing configuration data.
* [FIX] Improve state handling.

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
