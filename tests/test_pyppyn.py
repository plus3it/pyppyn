# test_pyppyn.py

import pytest

from pyppyn import ConfigRep

@pytest.fixture
def bad_configrep():
    """Returns a ConfigRep instance with a bad config file"""
    return ConfigRep(setup_path="pathdoesnotexist")

def test_non_existing_config(bad_configrep):
    """ Gives an error when no/invalid setup file is provided. """
    with pytest.raises(FileNotFoundError):
        bad_configrep.read_config()

@pytest.fixture
def configrep():
    """Returns a ConfigRep instance using the included test.cfg file"""
    return ConfigRep(setup_path="tests/minipippy",platform="linux",verbose=True)

def test_app_name_version(configrep):
    """ Tests reading the config file. """
    configrep.load_config()
    assert configrep.app_name == "minipippy" and configrep.app_version == "4.8.2"

def test_read_cfg_file(configrep):
    """ Tests reading the config file. """
    assert configrep.read_config()

def test_load_cfg_file(configrep):
    """ Tests load the config file. """
    configrep.read_config()
    assert configrep.load_config()

def test_install_packages(configrep):
    """ Tests installing the indicated packages. """
    configrep.read_config()
    configrep.load_config()
    assert configrep.install_packages()

def test_process_config(configrep):
    """ Tests installing the indicated packages. """
    assert configrep.process_config()

def test_get_required(configrep):
    """ Tests getting list of requirements. """
    assert set(configrep.get_required()) == set(['backoff', 'click', 'six', 'pyyaml']) 

def test_install_and_import():
    """ Tests the class method. """
    assert ConfigRep.install_and_import("pyyaml") == "yaml"

def test_package_to_module():
    """ Tests the class method. """
    assert ConfigRep.package_to_module("pyyaml") == "yaml"   

def test_get_config_attr(configrep):
    """ Tests getting an attribute from the configuration """
    assert configrep.get_config_attr('packages') == "minipippy"

def test_get_config_list(configrep):
    """ Tests getting a list from the configuration """
    assert set(configrep.get_config_list('platform')) == set(['Linux', 'Windows'])
