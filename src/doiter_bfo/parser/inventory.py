import importlib
import logging

from doiter_bfo.parser import Parser
from doiter_bfo.model.inventory import Inventory

_logger = logging.getLogger('InvetoryParser')


class InventoryParser(Parser):
    """
    Inventory Parser class
    Provide ability to parse DSL format like
    {host
        :name my_host
        :ssh_key ~/.ssh/id_rsa
    }
    """

    def _generate_kinds(self):
        """
        Generate kinds dict in next format:
        _kinds = {'template': Template,
                  'file': Template,
                  'package': Package,
                  'service': Service,
                  'command': Command}
        """
        self._kinds = {'host': Inventory}
