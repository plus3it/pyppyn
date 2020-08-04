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
import logging
import logging.config
import os
import platform
import shutil
import subprocess
import sys
import uuid
import zipfile

__version__ = "0.3.34"

__EXITOKAY__ = 0
FILE_DIR = ".pyppyn"

logging.config.fileConfig(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.conf'))
logger = logging.getLogger(__name__)        # pylint: disable=invalid-name


class ConfigRep():
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
        config: A dict representing the values in the config
            file.
        python_version: A float with the major and minor versions of
            the currently running python.
        reqs: A list of packages required for the given package.

    """

    WHEEL_TEMP_DIR = "temp"
    STATE_INIT = "INIT"
    STATE_READ = "READ"
    STATE_LOAD = "LOAD"
    STATE_INSTALLED = "INSTALLED"

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
        self._status = {}
        self._status['should_load'] = 0
        self._status['did_load'] = 0
        self._status['state'] = ConfigRep.STATE_INIT

        # Initial values
        self.setup_path = kwargs.get('setup_path', ".")
        self.platform = kwargs.get('platform', platform.system()).lower()

        # Logging
        logger.info("Platform: %s", self.platform)
        logger.info("Setup path: %s", self.setup_path)

        # will hold configuration attributes
        self.config = {}
        self.config['app_name'] = None
        self.config['app_version'] = None

        # system
        self.python_version = sys.version_info[0] + (sys.version_info[1] / 10)

        # requirements
        self.reqs = {
            'os': [],
            'other': [],
            'base': [],
            'python': [],
            'unparsed': []}

        # suffix for renaming build/dist directories
        self._rename_end = None

    def process_config(self):
        """Perform all steps with one call."""
        return self.read_config() and \
            self.load_config() and \
            self.install_packages()

    def _create_wheel(self):
        # if build and/or dist directories already exist, rename
        self._rename_end = '_' + uuid.uuid1().hex[:16]
        if os.path.isdir(os.path.join(self.setup_path, 'build')):
            os.rename(
                os.path.join(self.setup_path, 'build'),
                os.path.join(self.setup_path, 'build' + self._rename_end)
            )

        if not os.path.isdir(os.path.join(self.setup_path, FILE_DIR)):
            os.makedirs(os.path.join(self.setup_path, FILE_DIR))

        logger.info("Building wheel from %s", self.setup_path)

        # actual wheel creation
        commands = [
            'python', 'setup.py', 'bdist_wheel', '--universal', '--bdist-dir',
            os.path.join(self.setup_path, FILE_DIR, 'temp'), '--dist-dir',
            os.path.join(self.setup_path, FILE_DIR, 'dist')]
        sub_return = subprocess.run(commands, check=False)
        if sub_return.returncode != 0:
            logger.error("Pyppyn could not setup package. Wheel build failed!")
            raise ChildProcessError

        os.chdir(os.path.join(self.setup_path, FILE_DIR, 'dist'))

        logger.info("Extracting wheel (unzipping)")

        wheel_file = None

        for wheel_file in glob.glob(os.path.join('.', '*whl')):
            logger.info("Wheel archive found: %s", wheel_file)

        if wheel_file is not None:
            logger.info("Unzipping: %s", wheel_file)
            zip_ref = zipfile.ZipFile(wheel_file, 'r')
            zip_ref.extractall(ConfigRep.WHEEL_TEMP_DIR)
            zip_ref.close()

    def _wheel_directories(self):
        # look at directories wheel created
        logger.info("Going through wheel directories")
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
        logger.info("Looking at wheel top level")
        self.config["top_level"] = open("top_level.txt", "r").read().strip()

    def _wheel_console_scripts(self):
        # console scripts
        logger.info("Reading names of console scripts")
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
        logger.info("Reading wheel metadata")
        bulk = open("METADATA", "r").read()
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
        logger.info("Cleaning up wheel")

        if os.path.isdir(os.path.join(self.setup_path, 'build')):
            shutil.rmtree(os.path.join(self.setup_path, 'build'))

        if os.path.isdir(os.path.join(self.setup_path, FILE_DIR)):
            shutil.rmtree(os.path.join(self.setup_path, FILE_DIR))

        if os.path.isdir(
                os.path.join(self.setup_path, 'build' + self._rename_end)):
            os.rename(os.path.join(
                self.setup_path,
                'build' + self._rename_end
            ), os.path.join(self.setup_path, 'build'))

    def read_config(self):
        """Create wheel from the setup path given and read metadata."""
        logger.info("Reading configuration of %s", self.setup_path)

        # check for existence of setup.py, required
        if not os.path.isfile(os.path.join(self.setup_path, 'setup.py')):
            logger.info("setup.py not found at %s", self.setup_path)
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
        self._status['state'] = ConfigRep.STATE_READ
        return self.config is not None

    def _parse_marker(self, package=None, marker=None):
        """Parse the markers.

        Plain markers have 3 parts, 1. key, 2. conditional, 3. value
        Compound markers (not supported) have multiple markers, such as:
        platform_system == "Windows" and python_version == "2.7"
        https://github.com/pypa/setuptools/blob/master/pkg_resources/_vendor/packaging/markers.py
        https://www.python.org/dev/peps/pep-0496/

        """
        package = package.strip()

        marker_parts = marker.split(' ')

        # get rid of quotes and whitespace on markers
        for i, mark_part in enumerate(marker_parts):
            marker_parts[i] = mark_part.strip().strip('"').strip("'").strip()

        if len(marker_parts) != 3:
            logger.info("Unsupported marker [%s]: %s", package, marker)
            self.reqs['unparsed'].append(package)

        elif marker_parts[0] == 'platform_system' \
                and marker_parts[1] == '==' \
                and marker_parts[2].lower() == self.platform:
            self.reqs['os'].append(package)

        elif marker_parts[0] == 'platform_system' \
                and marker_parts[1] == '==' \
                and marker_parts[2].lower() != self.platform:
            self.reqs['other'].append(package)

        elif marker_parts[0] == 'python_version':
            if marker_parts[1] == '<' \
                    and self.python_version < float(marker_parts[2]):
                self.reqs['python'].append(package)
            elif marker_parts[1] == '>' \
                    and self.python_version > float(marker_parts[2]):
                self.reqs['python'].append(package)
            elif marker_parts[1] == '>=' \
                    and self.python_version >= float(marker_parts[2]):
                self.reqs['python'].append(package)
            elif marker_parts[1] == '<=' \
                    and self.python_version <= float(marker_parts[2]):
                self.reqs['python'].append(package)
            elif marker_parts[1] == '!=' \
                    and self.python_version != float(marker_parts[2]):
                self.reqs['python'].append(package)
            elif marker_parts[1] == '==' \
                    and self.python_version == float(marker_parts[2]):
                self.reqs['python'].append(package)

        else:
            self.reqs['unparsed'].append(package)

    def load_config(self):
        """Load the config file into data structures."""
        # Check that config has been read
        if self._status['state'] != ConfigRep.STATE_READ:
            self.read_config()

        self.config['app_name'] = self.config["metadata"]["name"][0]
        self.config['app_version'] = str(
            self.config["metadata"]["version"][0]
        ).lower()

        logger.info("This Python version: %s", self.python_version)
        logger.info(
            "Version from %s: %s", self.setup_path, self.config['app_version']
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
                self.reqs['base'].append(req.lower())

        logger.info("Install Requires:")
        logger.info("\tGenerally required: %s", self.reqs['base'])
        logger.info("\tFor this OS: %s", self.reqs['os'])
        logger.info("\tFor this Python version: %s", self.reqs['python'])
        logger.info("\tUnparsed markers: %s", self.reqs['unparsed'])
        logger.info(
            "\tOthers listed but not required (e.g., wrong platform): %s",
            self.reqs['other']
        )

        self._status['should_load'] = len(self.reqs['base']) \
            + len(self.reqs['os']) \
            + len(self.reqs['python']) \
            + len(self.reqs['unparsed'])

        self._status['state'] = ConfigRep.STATE_LOAD

        return self._status['should_load'] > 0

    def install_packages(self):
        """Install all needed packages from the config file."""
        if self._status['state'] != ConfigRep.STATE_LOAD:
            self.load_config()

        for package in self.reqs['os'] \
                + self.reqs['python'] \
                + self.reqs['base'] \
                + self.reqs['unparsed']:
            logger.info("Installing package: %s", package)
            if ConfigRep.install_package(package):
                self._status['did_load'] += 1

        self._status['state'] = ConfigRep.STATE_INSTALLED

        return self._status['did_load'] == self._status['should_load']

    def get_required(self):
        """Return required packages based on configuration."""
        if self._status['state'] != ConfigRep.STATE_LOAD \
                and self._status['state'] != ConfigRep.STATE_INSTALLED:
            self.load_config()

        return self.reqs['base'] \
            + self.reqs['os'] \
            + self.reqs['python'] \
            + self.reqs['unparsed']

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
        if self._status['state'] != ConfigRep.STATE_LOAD \
                and self._status['state'] != ConfigRep.STATE_INSTALLED:
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
        if self._status['state'] != ConfigRep.STATE_LOAD \
                and self._status['state'] != ConfigRep.STATE_INSTALLED:
            self.load_config()

        return self.config.get(key, self.config['metadata'].get(key, [None]))
