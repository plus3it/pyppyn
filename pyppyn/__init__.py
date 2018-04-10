# -*- coding: utf-8 -*-
"""pyppyn module"""

"""pyppyn is small but mighty.
PIPPIN: I didn't think it would end this way.
GANDALF: End? No, the journey doesn't end here. Death is just another path, one that we all must take."""

import platform
import sys

from setuptools.config import read_configuration
from pkg_resources import parse_requirements

class ConfigRep:
    """Represents an interpretation of a setup.cfg file."""

    def __init__(self, *args, **kwargs):
        """Instantiation"""
        self.setup_file = kwargs.get('setup_file',"setup.cfg")
        self.platform = kwargs.get('platform',platform.system()).lower()
        #self.platform = "linux"

    def read_setup(self):
        self.config_dict = read_configuration(self.setup_file)

    def install_and_import(self, package):
        import importlib
        try:
            importlib.import_module(package)
        except ImportError:
            import pip
            pip.main(['install', package])
            print("Installing", package)
        finally:
            globals()[package] = importlib.import_module(package)

    def process_setup(self):
        self.python_version = sys.version_info[0] + (sys.version_info[1]/10)
        self.app_version = str(self.config_dict["metadata"]["version"]).lower()

        """ Parsing the most likely (but not all) possible markers
        Compound markers (e.g., 'platform_system == "Windows" and python_version < "2.7"') and
        conditional markers (e.g., "pywin32 >=1.0 ; sys_platform == 'win32'") are not
        supported yet. """
        self.this_os_reqs = []      # Requirements on this os/env
        self.other_reqs = []        # Not required on this os/env
        self.base_reqs = []         # Across the board reqs
        self.this_python_reqs = []  # This python version reqs

        for r in parse_requirements(self.config_dict["options"]["install_requires"]):
            if str(getattr(r, 'marker', 'None')) != 'None':
                """ Plain markers have 3 parts, 1. key, 2. conditional, 3. value
                Compound markers (not supported) will produce 3 markers,
                1. platform_system == "Windows", 2. and, 3. python_version == "2.7"
                https://github.com/pypa/setuptools/blob/master/pkg_resources/_vendor/packaging/markers.py
                https://www.python.org/dev/peps/pep-0496/ """
                for m in r.marker._markers:
                    if str(m[0]) == 'platform_system' and str(m[1]) == '==' and str(m[2]).lower() == self.platform:
                        self.this_os_reqs.append(r.key)
                    elif str(m[0]) == 'platform_system' and str(m[1]) == '==' and str(m[2]).lower() != self.platform:
                        self.other_reqs.append(r.key)
                    elif str(m[0]) == 'python_version':
                        if str(m[1]) == '<' and self.python_version < float(str(m[2])):
                            self.this_python_reqs.append(r.key)
                        elif str(m[1]) == '>' and self.python_version > float(str(m[2])):
                            self.this_python_reqs.append(r.key)
                        elif str(m[1]) == '>=' and self.python_version >= float(str(m[2])):
                            self.this_python_reqs.append(r.key)
                        elif str(m[1]) == '<=' and self.python_version <= float(str(m[2])):
                            self.this_python_reqs.append(r.key)
                        elif str(m[1]) == '!=' and self.python_version != float(str(m[2])):
                            self.this_python_reqs.append(r.key)
                        elif str(m[1]) == '==' and self.python_version == float(str(m[2])):
                            self.this_python_reqs.append(r.key)
                        else:
                            self.other_reqs.append(r.key)
                    else:
                        self.base_reqs.append(r.key) # if can't figure out the marker, add it
            else:
                self.base_reqs.append(r.key)

        print("Requirements:")
        print("\tThis OS", self.this_os_reqs)
        print("\tOther", self.other_reqs)
        print("\tThis python", self.this_python_reqs)
        print("\tBase", self.base_reqs)

    def import_packages(self):
        for package in self.this_os_reqs :
            self.install_and_import(package)
        for package in self.this_python_reqs :
            self.install_and_import(package)
        for package in self.base_reqs :
            self.install_and_import(package)

