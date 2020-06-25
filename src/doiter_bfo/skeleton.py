# -*- coding: utf-8 -*-
"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
[options.entry_points] section in setup.cfg:

    console_scripts =
        bfo = doiter_bfo.skeleton:run

Then run `python setup.py install` which will install the command `bfo`
inside your current environment.
Besides console scripts, the header (i.e. until _logger...) of this file can
also be used as template for Python modules.

Note: This skeleton file can be safely removed if not needed!
"""

import argparse
import sys
import importlib
import logging

from doiter_bfo import __version__
from doiter_bfo.parser import Parser
from doiter_bfo.parser.inventory import InventoryParser
from doiter_bfo.operations.pyinfra import Pyinfra

from pyinfra.api.connectors.ssh import make_names_data as make_names_data_ssh

__author__ = 'vkropotko'
__copyright__ = 'vkropotko'
__license__ = 'mit'

_logger = logging.getLogger(__name__)


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description='BFO')
    parser.add_argument(
        '--version',
        action='version',
        version='doiter-bfo {ver}'.format(ver=__version__))
    parser.add_argument(
        dest='f',
        help='BFO manifest',
        type=str,
        metavar='file')
    parser.add_argument(
        dest='i',
        help='BFO inventory',
        type=str,
        metavar='inventory')
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = '[%(asctime)s] %(levelname)s:%(name)s:%(message)s'
    logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                        format=logformat, datefmt='%Y-%m-%d %H:%M:%S')


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    setup_logging(logging.INFO)

    inventory = InventoryParser()
    hosts = inventory.parse_file(args.i)

    prepared_hosts = []
    for host in hosts:
        prepared_host = next(make_names_data_ssh(host.get_connect_address()))
        for key, value in host.host_facts().items():
            prepared_host[1][key] = value
        prepared_hosts.append(prepared_host)

    pyinfra = Pyinfra(
        make_names_data=prepared_hosts
    )

    parser = Parser()
    blocks = parser.parse_file(args.f)

    operations = {}

    for block in blocks:
        block_class_name = block.__class__.__name__

        if block_class_name.endswith('Model'):
            operation_class = block_class_name[:-5].lower()

            if operation_class not in operations.keys():
                operation_module = importlib.import_module(
                    f'doiter_bfo.operations.{operation_class}')
                operations[operation_class] = getattr(
                    operation_module, operation_class.capitalize())

            add_action = operations[operation_class](**block.__dict__)

        _logger.info(add_action(pyinfra=pyinfra, apply=False))

    pyinfra.apply()

    _logger.info('Script ends here')


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
