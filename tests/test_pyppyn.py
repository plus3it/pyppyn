# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""pyppyn test script."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

import platform

import pytest

from pyppyn import ConfigRep


@pytest.fixture
def bad_configrep():
    """Return a ConfigRep instance with a bad config file."""
    return ConfigRep(setup_path="pathdoesnotexist")


def test_non_existing_config(bad_configrep):
    """Give an error when no/invalid setup file is provided."""
    with pytest.raises(FileNotFoundError):
        bad_configrep.read_config()


@pytest.fixture
def configrep():
    """Return a ConfigRep instance using the included minipippy package."""
    return ConfigRep(setup_path="tests/minipippy")


def test_app_name_version(configrep):
    """Test reading the config file."""
    configrep.load_config()
    assert (
        configrep.config["app_name"] == "minipippy"
        and configrep.config["app_version"] == "4.8.2"
    )


def test_read_cfg_file(configrep):
    """Test reading the config file."""
    assert configrep.read_config()


def test_load_cfg_file(configrep):
    """Test load the config file."""
    configrep.read_config()
    assert configrep.load_config()


def test_install_packages(configrep):
    """Test installing the indicated packages."""
    configrep.read_config()
    configrep.load_config()
    assert configrep.install_packages()


def test_process_config(configrep):
    """Test installing the indicated packages."""
    assert configrep.process_config()


def test_get_required(configrep):
    """Test getting list of requirements, including extra packages
    (such as those marked with "test", "check", "docs")."""
    if platform.system().lower() == "windows":
        assert set(configrep.get_required()) == set(
            [
                "backoff",
                "click",
                "pyyaml",
                "defusedxml",
                "pypiwin32",
                "six",
                "pytest",
                "flake8",
                "sphinx",
            ]
        )
    else:
        assert set(configrep.get_required()) == set(
            ["backoff", "click", "six", "pyyaml", "pytest", "flake8", "sphinx"]
        )


def test_get_required_no_extras(configrep):
    """Test getting list of requirements."""
    if platform.system().lower() == "windows":
        assert set(configrep.get_required(include_extras_require=False)) == set(
            ["backoff", "click", "pyyaml", "defusedxml", "pypiwin32", "six"]
        )
    else:
        assert set(configrep.get_required(include_extras_require=False)) == set(
            ["backoff", "click", "six", "pyyaml"]
        )


def test_install_package():
    """Test the class method."""
    assert ConfigRep.install_package("pyyaml")


def test_get_config_attr(configrep):
    """Test getting an attribute from the configuration."""
    assert configrep.get_config_attr("packages") == "minipippy"


def test_get_config_list(configrep):
    """Test getting a list from the configuration."""
    assert set(configrep.get_config_list("platform")) == set(["Linux", "Windows"])
