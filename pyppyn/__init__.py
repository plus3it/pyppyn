# -*- coding: utf-8 -*-
"""Pyppyn module.

This module helps give programmatic access to the setup configuration
of a package and allows automatic installation of required packages.
This can be useful for automated environments.

This module can be used by python scripts or through the included command-
line interface (CLI).

Pyppyn, like the hobbit, is small but mighty. This module is named in
honor of Pippin, a companion, friend, Bichon Frise-Shih Tzu mix. He
passed away on March 30, 2018 at the age of 12 after a battle with
diabetes, blindness, deafness, and loss of smell. Pleasant to the
end, he was a great, great dog.
PIPPIN: I didn't think it would end this way.
GANDALF: End? No, the journey doesn't end here. Death is just another
    path, one that we all must take.

Example:
    Help using the Pyppyn CLI can be found by typing the following::

        $ pyppyn --help
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import glob
import importlib
import os
import platform
import shutil
import subprocess
import sys
import uuid
import zipfile

__version__ = "0.3.4"

__EXITOKAY__ = 0


class ConfigRep(object):
    """Utility for reading setup.cfg and installing dependencies.

    This class helps find packages that must be installed as
    dependencies of a given package, based on a configuration file.
    In automated environments or when using automation to create
    standalone applications, it can be helpful to have programmatic
    access to this information.

    Attributes:
        setup_path: A str of the path to process (where setup.py and
            setup.cfg are located).
        platform: A str of the platform. This is automatically
            determined or can be overriden.
        verbose: A bool of whether to display extra messages.
        config: A dict representing the values in the config
            file.
        python_version: A float with the major and minor versions of
            the currently running python.
        app_version: A str of the version represented by the config
            file.
        os_reqs: A list of packages required for this os/env.
        other_reqs: A list of packages that are not required.
            Included for debug so that it is possible to see where
            everything went.
        base_reqs: A list of non-specific requirements that are also
            needed.
        python_reqs: A list of packages required for this
            version of python.
        unparsed_reqs: A list of packages with markers that could
            not be parsed.

    """

    WHEEL_TEMP_DIR = "temp"
    STATE_INIT = "INIT"
    STATE_READ = "READ"
    STATE_LOAD = "LOAD"
    STATE_INSTALLED = "INSTALLED"
    VERB_MESSAGE_PREFIX = "[Pyppyn]"

    verbose = False

    @classmethod
    def verboseprint(cls, *a, **k):
        """Print a verbose message."""
        if cls.verbose:
            print(cls.VERB_MESSAGE_PREFIX, *a, **k)

    @classmethod
    def install_package(cls, package):
        """Installs a package.

        Args:
            package: A str of the package to install.

        Returns:
            True on success.

        """
        success = subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', package]
        )

        if success != 0:
            return False

        return True

    @classmethod
    def import_module(cls, module):
        """Import a module.

        Args:
            module: A str of the module to import.

        Returns:
            True on success.

        """
        try:
            globals()[module] = importlib.import_module(module)

        except ImportError:
            return False

        return True

    def __init__(self, **kwargs):
        """Instantiate."""
        # global __VERBOSE__
        self._should_load = 0
        self._did_load = 0
        self._state = ConfigRep.STATE_INIT

        # Initial values
        self.setup_path = kwargs.get('setup_path', ".")
        self.platform = kwargs.get('platform', platform.system()).lower()
        ConfigRep.verbose = kwargs.get('verbose', False)

        # Verbose output
        ConfigRep.verboseprint("Verbose mode")
        ConfigRep.verboseprint("Platform:", self.platform)
        ConfigRep.verboseprint("Setup path:", self.setup_path)

        # will hold configuration attributes
        self.config = {}

        # system
        self.python_version = sys.version_info[0] + (sys.version_info[1] / 10)

        # app
        self.app_name = None
        self.app_version = None

        # requirements
        self.os_reqs = []           # Requirements on this os/env
        self.other_reqs = []        # Not required on this os/env
        self.base_reqs = []         # Across the board reqs
        self.python_reqs = []       # This python version reqs
        self.unparsed_reqs = []     # Couldn't figure out marker

        # suffix for renaming build/dist directories
        self._rename_end = None

    def process_config(self):
        """Perform all steps with one call."""
        return self.read_config() and \
            self.load_config() and \
            self.install_packages()

    def _create_wheel(self):
        ConfigRep.verboseprint("Building wheel from", self.setup_path)
        # if build and/or dist directories already exist, rename
        self._rename_end = '_' + uuid.uuid1().hex[:16]

        if os.path.isdir(os.path.join(self.setup_path, 'build')):
            os.rename(
                os.path.join(self.setup_path, 'build'),
                os.path.join(self.setup_path, 'build' + self._rename_end)
            )
        if os.path.isdir(os.path.join(self.setup_path, 'dist')):
            os.rename(
                os.path.join(self.setup_path, 'dist'),
                os.path.join(self.setup_path, 'dist' + self._rename_end)
            )

        # actual wheel creation
        commands = ['python', 'setup.py', 'bdist_wheel', '--universal']
        sub_return = subprocess.run(commands, check=True)
        if sub_return.returncode != 0:
            ConfigRep.verboseprint("Wheel build failed")
            raise ChildProcessError

        os.chdir('dist')

        ConfigRep.verboseprint("Extracting wheel (unzipping)")

        wheel_file = None

        for wheel_file in glob.glob(os.path.join('.', '*whl')):
            ConfigRep.verboseprint("Wheel archive found:", wheel_file)

        if wheel_file is not None:
            ConfigRep.verboseprint("Unzipping:", wheel_file)
            zip_ref = zipfile.ZipFile(wheel_file, 'r')
            zip_ref.extractall(ConfigRep.WHEEL_TEMP_DIR)
            zip_ref.close()

    def _wheel_directories(self):
        # look at directories wheel created
        ConfigRep.verboseprint("Going through wheel directories")
        self.config["packages"] = []
        for created_file in glob.glob(os.path.join('.', '*')):

            if not created_file.endswith('.dist-info') \
                    and os.path.isdir(created_file):
                if created_file.startswith('.' + os.sep):
                    created_file = created_file[2:]
                self.config["packages"].append(created_file)
            elif created_file.endswith('.dist-info'):
                self.config["metadata_dir"] = created_file

    def _wheel_top_level(self):
        # top level
        ConfigRep.verboseprint("Looking at wheel top level")
        self.config["top_level"] = open("top_level.txt", "r").read().strip()

    def _wheel_console_scripts(self):
        # console scripts
        ConfigRep.verboseprint("Reading names of console scripts")
        ep_file = open("entry_points.txt", "r")
        self.config["console_scripts"] = []
        console_scripts = False
        for line in ep_file:
            if line.startswith('[console_scripts]'):
                console_scripts = True
            elif console_scripts:
                parts = line.split(' = ')
                if len(parts) > 1:
                    self.config["console_scripts"].append(
                        parts[0].strip()
                    )

    def _wheel_metadata(self):
        # metadata
        ConfigRep.verboseprint("Reading wheel metadata")
        bulk = open("METADATA", "U").read()
        parts = bulk.split("\n\n")
        if len(parts) > 1:
            metadata = parts[0].strip()
        else:
            metadata = bulk

        self.config["metadata"] = {}
        for line in metadata.split("\n"):
            parts = line.split(': ', maxsplit=1)
            if len(parts) > 1:
                key = parts[0].strip().lower()
                value = parts[1].strip()
                if self.config["metadata"].get(key) is None:
                    self.config["metadata"][key] = [value]
                else:
                    self.config["metadata"][key].append(value)

    def _wheel_cleanup(self):
        # put back dist and build
        ConfigRep.verboseprint("Cleaning up wheel")
        shutil.rmtree(os.path.join(self.setup_path, 'build'))
        if os.path.isdir(os.path.join(
                self.setup_path,
                'build' + self._rename_end
        )):
            os.rename(os.path.join(
                self.setup_path,
                'build' + self._rename_end
            ), os.path.join(self.setup_path, 'build'))

        shutil.rmtree(os.path.join(self.setup_path, 'dist'))
        if os.path.isdir(os.path.join(
                self.setup_path,
                'dist' + self._rename_end
        )):
            os.rename(os.path.join(
                self.setup_path,
                'dist' + self._rename_end
            ), os.path.join(self.setup_path, 'dist'))

    def read_config(self):
        """Create wheel from the setup path given and read metadata."""
        ConfigRep.verboseprint("Reading configuration of", self.setup_path)

        # check for existence of setup.py, required
        if not os.path.isfile(os.path.join(self.setup_path, 'setup.py')):
            ConfigRep.verboseprint("setup.py not found at", self.setup_path)
            raise FileNotFoundError

        original_cwd = os.getcwd()

        # create wheel
        os.chdir(self.setup_path)
        self._create_wheel()

        os.chdir(ConfigRep.WHEEL_TEMP_DIR)
        self._wheel_directories()

        os.chdir(self.config["metadata_dir"])
        self._wheel_top_level()
        self._wheel_console_scripts()
        self._wheel_metadata()

        # go back to original directory
        os.chdir(original_cwd)
        self._wheel_cleanup()

        # self.config = config.read_configuration(self.setup_path)
        self._state = ConfigRep.STATE_READ
        return self.config is not None

    def _parse_marker(self, package=None, marker=None):
        """Parse the markers.

        Plain markers have 3 parts, 1. key, 2. conditional, 3. value
        Compound markers (not supported) have multiple markers, such as:
        platform_system == "Windows" and python_version == "2.7"
        https://github.com/pypa/setuptools/blob/master/pkg_resources/_vendor/packaging/markers.py
        https://www.python.org/dev/peps/pep-0496/

        """
        marker_parts = marker.split(' ')

        # get rid of quotes and whitespace on markers
        for i, mark_part in enumerate(marker_parts):
            marker_parts[i] = mark_part.strip().strip('"').strip("'").strip()

        if len(marker_parts) != 3:
            ConfigRep.verboseprint(
                "Unsupported marker [",
                package,
                "]:",
                marker
            )
            self.unparsed_reqs.append(package)

        elif marker_parts[0] == 'platform_system' \
                and marker_parts[1] == '==' \
                and marker_parts[2].lower() == self.platform:
            self.os_reqs.append(package)

        elif marker_parts[0] == 'platform_system' \
                and marker_parts[1] == '==' \
                and marker_parts[2].lower() != self.platform:
            self.other_reqs.append(package)

        elif marker_parts[0] == 'python_version':
            if marker_parts[1] == '<' \
                    and self.python_version < float(marker_parts[2]):
                self.python_reqs.append(package)
            elif marker_parts[1] == '>' \
                    and self.python_version > float(marker_parts[2]):
                self.python_reqs.append(package)
            elif marker_parts[1] == '>=' \
                    and self.python_version >= float(marker_parts[2]):
                self.python_reqs.append(package)
            elif marker_parts[1] == '<=' \
                    and self.python_version <= float(marker_parts[2]):
                self.python_reqs.append(package)
            elif marker_parts[1] == '!=' \
                    and self.python_version != float(marker_parts[2]):
                self.python_reqs.append(package)
            elif marker_parts[1] == '==' \
                    and self.python_version == float(marker_parts[2]):
                self.python_reqs.append(package)

        else:
            self.unparsed_reqs.append(package)

    def load_config(self):
        """Load the config file into data structures."""
        # Check that config has been read
        if self._state != ConfigRep.STATE_READ:
            self.read_config()

        self.app_name = self.config["metadata"]["name"][0]
        self.app_version = str(self.config["metadata"]["version"][0]).lower()

        ConfigRep.verboseprint("This Python:", self.python_version)
        ConfigRep.verboseprint(
            "Version from",
            self.setup_path,
            ":",
            self.app_version
        )

        # Parsing some (but not all) possible markers.
        # Compound markers (e.g., 'platform_system == "Windows" and
        # python_version < "2.7"') and
        # conditional markers (e.g., "pywin32 >=1.0 ; sys_platform == 'win32'")
        # are not supported yet.

        for req in self.config["metadata"]["requires-dist"]:

            parts = req.lower().split('; ')
            if len(parts) > 1:

                # marker present
                self._parse_marker(package=parts[0], marker=parts[1])

            else:
                self.base_reqs.append(req.lower())

        ConfigRep.verboseprint("Install Requires:")
        ConfigRep.verboseprint("\tGenerally required:", self.base_reqs)
        ConfigRep.verboseprint("\tFor this OS:", self.os_reqs)
        ConfigRep.verboseprint("\tFor this Python version:", self.python_reqs)
        ConfigRep.verboseprint("\tUnparsed markers:", self.unparsed_reqs)
        ConfigRep.verboseprint(
            "\tOthers listed by not required (e.g., wrong platform):",
            self.other_reqs
        )

        self._should_load = len(self.base_reqs) \
            + len(self.os_reqs) \
            + len(self.python_reqs) \
            + len(self.unparsed_reqs)

        self._state = ConfigRep.STATE_LOAD

        return self._should_load > 0

    def install_packages(self):
        """Install all needed packages from the config file."""
        if self._state != ConfigRep.STATE_LOAD:
            self.load_config()

        for package in self.os_reqs \
                + self.python_reqs \
                + self.base_reqs \
                + self.unparsed_reqs:
            ConfigRep.verboseprint("Installing package:", package)
            if ConfigRep.install_package(package):
                self._did_load += 1

        self._state = ConfigRep.STATE_INSTALLED

        return self._did_load == self._should_load

    def get_required(self):
        """Return required packages based on configuration."""
        if self._state != ConfigRep.STATE_LOAD \
                and self._state != ConfigRep.STATE_INSTALLED:
            self.load_config()

        return self.base_reqs \
            + self.os_reqs \
            + self.python_reqs \
            + self.unparsed_reqs

    def get_config_attr(self, key, element=0):
        """Return value associated with a key in the configuration.

        If not found directly under the
        configuration, a value from the metadata in the configuration
        is checked. In Pyppyn, all configuration attributes are
        lists. This method only returns the first value in the list,
        and de-listifies the value.

        Args:
            key: A str of the key for which you want a value from
                the configuration data.
            element: An integer representing the index of the list
                item to return [0].

        Returns:
            A str of the value associated with the attr OR None if
            it is not present.

        """
        if self._state != ConfigRep.STATE_LOAD \
                and self._state != ConfigRep.STATE_INSTALLED:
            self.load_config()

        return self.config.get(
            key,
            self.config['metadata'].get(key, [None])
        )[element]

    def get_config_list(self, key):
        """Return a list associated with a key in the configuration.

        In Pyppyn, all configuration
        attributes are lists. If no list is found in the main
        configuration, the metadata in the configuration is checked.

        Args:
            key: A str of the key for which you want a value from
                the configuration data.

        Returns:
            A str of the value associated with the attr OR None if
            it is not present.

        """
        if self._state != ConfigRep.STATE_LOAD \
                and self._state != ConfigRep.STATE_INSTALLED:
            self.load_config()

        return self.config.get(key, self.config['metadata'].get(key, [None]))
