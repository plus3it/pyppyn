======
Pyppyn
======

.. image:: https://img.shields.io/github/license/YakDriver/pyppyn.svg
    :target: ./LICENSE
    :alt: License
.. image:: https://travis-ci.org/YakDriver/pyppyn.svg?branch=master
    :target: http://travis-ci.org/YakDriver/pyppyn
    :alt: Build Status
.. image:: https://img.shields.io/pypi/pyversions/pyppyn.svg
    :target: https://pypi.python.org/pypi/pyppyn
    :alt: Python Version Compatibility
.. image:: https://img.shields.io/pypi/v/pyppyn.svg?label=version
    :target: https://pypi.python.org/pypi/pyppyn
    :alt: Version

Pyppyn helps you dynamically read setup configurations and load dependencies.

Since ``pip`` is excellent at reading setup configurations and loading dependencies, why Pyppyn?
If you need programmatic access to dependency information, for example, in dynamically creating standalone 
applications using `PyInstaller <http://www.pyinstaller.org>`_ Pyppyn can help you out.

Pyppyn can be used in scripts or using the CLI. Either way, it can be installed easily.

.. code-block:: bash

    $ pip install pyppyn

CLI
===

``Pyppyn`` will display help in typical fashion.

.. code-block:: bash

    $ pyppyn --help

Example
=======

To parse the included test ``setup.cfg`` file and install the required dependencies, you can
use this command. This allows you to install dependencies without installing the package associated with a given ``setup.cfg`` file.

.. code-block:: bash

    $ pyppyn --setup-file tests/test.cfg --platform linux -v -a
    Pyppyn CLI, 0.2.1
    [Pyppyn] Verbose mode
    [Pyppyn] Platform: linux
    [Pyppyn] Setup file: tests/test.cfg
    [Pyppyn] Reading config file: tests/test.cfg
    [Pyppyn] This Python: 3.6
    [Pyppyn] Version from tests/test.cfg : 0.9.4.dev
    [Pyppyn] Install Requires:
    [Pyppyn] 	Generally required: ['backoff', 'click', 'six', 'pyyaml']
    [Pyppyn] 	For this OS: []
    [Pyppyn] 	For this Python version: []
    [Pyppyn] 	Others listed by not required (e.g., wrong platform): ['defusedxml', 'futures', 'pypiwin32', 'wheel']
    [Pyppyn] Installed: backoff
    [Pyppyn] Imported: backoff
    [Pyppyn] Installed: click
    [Pyppyn] Imported: click
    [Pyppyn] Installed: six
    [Pyppyn] Imported: six
    [Pyppyn] Installed: pyyaml
    [Pyppyn] Imported: yaml

From Python
===========

This is a sample usage of Pyppyn from a Python script.

.. code-block:: python

    import pyppyn

    # Create an instance
    p = pyppyn.ConfigRep(setup_file="tests/test.cfg",verbose=True)

    # Load config, install dependencies and import a module from the package
    p.process_config()

    print("Package requires:", p.this_os_reqs + p.this_python_reqs + p.base_reqs)

Contribute
==========

``Pyppyn`` is hosted on `GitHub <http://github.com/YakDriver/pyppyn>`_ and is an open source project that welcomes contributions of all kinds from the community.

For more information about contributing, see `the contributor guidelines <https://github.com/YakDriver/pyppyn/CONTRIBUTING.rst>`_.

Namesake
========

This module is named in
honor of Pippin, a companion, friend, Bichon Frise-Shih Tzu mix. He
passed away on March 30, 2018 at the age of 12 after a battle with
diabetes, blindness, deafness, and loss of smell. Pleasant to the
end, he was a great, great dog.

