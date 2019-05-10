======
Pyppyn
======

.. image:: https://img.shields.io/github/license/plus3it/pyppyn.svg
    :target: ./LICENSE
    :alt: License
.. image:: https://travis-ci.org/plus3it/pyppyn.svg?branch=master
    :target: http://travis-ci.org/plus3it/pyppyn
    :alt: Build Status
.. image:: https://img.shields.io/pypi/pyversions/pyppyn.svg
    :target: https://pypi.python.org/pypi/pyppyn
    :alt: Python Version Compatibility
.. image:: https://img.shields.io/pypi/v/pyppyn.svg
    :target: https://pypi.python.org/pypi/pyppyn
    :alt: Version
.. image:: https://pullreminders.com/badge.svg
    :target: https://pullreminders.com?ref=badge
    :alt: Pull Reminder

Pyppyn helps you dynamically read setup configurations and load dependencies.

Since ``pip`` is excellent at reading setup configurations and loading dependencies, why Pyppyn?
If you need programmatic access to dependency information, for
example, in dynamically creating standalone
applications using `GravityBee <https://github.com/plus3it/gravitybee>`_ and `PyInstaller <http://www.pyinstaller.org>`_, Pyppyn can help you out.

Pyppyn can be used in scripts or using the CLI. Either way, it can be
installed easily.

.. code-block:: bash

    $ pip install pyppyn

CLI
===

``Pyppyn`` will display help in typical fashion.

.. code-block:: bash

    $ pyppyn --help

Example
=======

To parse the included test mini Python package (tests/minipippy),
with a setup.cfg and setup.py file, and install the required
dependencies, you can use this command. This allows you to install
dependencies without installing the package.

.. code-block:: bash

    $ pyppyn --setup-path tests/minipippy --platform linux -v -a
    Pyppyn CLI, 0.3.5
    [Pyppyn] Platform: linux
    [Pyppyn] Setup path: tests/minipippy
    [Pyppyn] Reading configuration of tests/minipippy
    [Pyppyn] Building wheel from tests/minipippy
    [...]
    [Pyppyn] Extracting wheel (unzipping)
    [Pyppyn] Wheel archive found: ./minipippy-4.8.2-py2.py3-none-any.whl
    [Pyppyn] Unzipping: ./minipippy-4.8.2-py2.py3-none-any.whl
    [Pyppyn] Going through wheel directories
    [Pyppyn] Looking at wheel top level
    [Pyppyn] Reading names of console scripts
    [Pyppyn] Reading wheel metadata
    [Pyppyn] Cleaning up wheel
    [Pyppyn] This Python: 3.6
    [Pyppyn] Version from tests/minipippy : 4.8.2
    [Pyppyn] Unsupported marker [ six ]: platform_system == "linux" and python_version > "3.3"
    [Pyppyn] Install Requires:
    [Pyppyn] 	Generally required: ['backoff', 'click', 'pyyaml']
    [Pyppyn] 	For this OS: []
    [Pyppyn] 	For this Python version: []
    [Pyppyn] 	Unparsed markers: ['six']
    [Pyppyn] 	Others listed by not required (e.g., wrong platform): ['defusedxml', 'pypiwin32']
    [Pyppyn] Installing package: backoff
    [Pyppyn] Imported module: backoff
    [Pyppyn] Installing package: click
    [Pyppyn] Imported module: click
    [Pyppyn] Installing package: pyyaml
    [Pyppyn] Imported module: yaml


From Python
===========

This is a sample usage of Pyppyn from a Python script.

.. code-block:: python

    import pyppyn

    # Create an instance
    p = pyppyn.ConfigRep(setup_path="tests/minipippy")

    # Load config, install dependencies and import a module from the package
    p.process_config()

    print("Package requires:", p.get_required())

Contribute
==========

``Pyppyn`` is hosted on `GitHub <http://github.com/plus3it/pyppyn>`_ and is an open source project that welcomes contributions of all kinds from the community.

For more information about contributing, see `the contributor guidelines <CONTRIBUTING.md>`_.

Namesake
========

This module is named in
honor of Pippin, a companion, friend, Bichon Frise-Shih Tzu mix. He
passed away on March 30, 2018 at the age of 12 after a battle with
diabetes, blindness, deafness, and loss of smell. Pleasant to the
end, he was a great, great dog.

