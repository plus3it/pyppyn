# -*- coding: utf-8 -*-
"""pyppyn cli."""
import os
import platform
import sys

import click

from pyppyn import ConfigRep

click.disable_unicode_literals_warning = True

@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
#@click.version_option(version=pyppyn.__version__)
@click.option('-p', '--process-setup', 'process-setup', default=None,
              help=(
                  'Process the setup '))

def main(extra_arguments=None, **kwargs):
    """Entry point for pyppyn cli."""
    p = ConfigRep(setup_file="test.cfg")
    print("Setup file",p.setup_file)
    print("OS",p.platform)
    p.read_setup()
    p.process_setup()

    sys.exit()