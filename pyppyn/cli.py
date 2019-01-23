# -*- coding: utf-8 -*-
"""pyppyn cli."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import sys

import click

import pyppyn

click.disable_unicode_literals_warning = True


@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.version_option(version=pyppyn.__version__)
@click.option('--setup-path', '-s', 'setup_path', default='.',
              help='Name of the path containing setup.py.')
@click.option('--platform', '-p', 'platform', default=None,
              help='Defaults to the current machine, use this option \
              to override (e.g., Windows or Linux).')
@click.option('--auto-load', '-a', 'auto_load', is_flag=True,
              help='Install, if necessary, and import all required \
              packages.')
@click.option('--display', '-d', 'display', is_flag=True,
              help='Display package information but do not install or \
              import packages.')
def main(**kwargs):
    """Entry point for Pyppyn CLI."""
    print("Pyppyn CLI,", pyppyn.__version__)

    # Remove unused options
    empty_keys = [k for k, v in kwargs.items() if not v]
    for k in empty_keys:
        del kwargs[k]

    exit_val = pyppyn.__EXITOKAY__

    # Create an instance
    pyppyn_instance = pyppyn.ConfigRep(**kwargs)

    if kwargs.get('display', False):
        if not (
                pyppyn_instance.read_config() and
                pyppyn_instance.load_config()
        ):
            exit_val = 1

    elif kwargs.get('auto_load', False):
        if not pyppyn_instance.process_config():
            exit_val = 1

    sys.exit(exit_val)
