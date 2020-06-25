import importlib
import logging

from pyparsing import Word, alphanums, Group, OneOrMore, Suppress, ZeroOrMore
from doiter_bfo.model import BaseBlock

_logger = logging.getLogger('Parser')


class Parser:
    """
    Parser class
    Provide ability to parse DSL format like
    {file
        :name testfile
        :path /var/tmp/testfile
        :content none
        :exists
        :depends package:vim
    }
    {package
        :name vim
        :installed
    }
    """
    _param_value_chrs = ''.join(chr(c) for c in range(65536) if chr(c) not in [
        '{', '}', ':', '"'] and not chr(c).isspace())

    _param_value_string = ''.join(chr(c)
                                  for c in range(65536) if chr(c) != '"')

    def _generate_kinds(self):
        """
        Generate kinds dict in next format:
        _kinds = {'template': Template,
                  'file': Template,
                  'package': Package,
                  'service': Service,
                  'command': Command}
        """
        self._kinds = {}
        models_mod = importlib.import_module('doiter_bfo.model')
        models = [model for model in dir(
            models_mod) if model.endswith('Model')]
        for model_name in models:
            # Create short name from Model name, e.g. ServiceModel -> Service
            model_name_short = model_name[:-5]
            self._kinds[model_name_short.lower()] = getattr(
                models_mod, model_name)

    def __init__(self):
        self._generate_kinds()
        self._parser = OneOrMore(
            Group(
                Suppress('{') +
                Word(alphanums) +
                OneOrMore(
                    Group(
                        Word(':' + alphanums + '_' + '-') +
                        ZeroOrMore(
                            Word(self._param_value_chrs) ^
                            Suppress(
                                '"') + Word(self._param_value_string) + Suppress('"')
                        )
                    )
                ) +
                Suppress('}')
            )
        )

    def _get_kind(self, param: str) -> BaseBlock:
        if param:
            if param in self._kinds.keys():
                return self._kinds[param]
        return None

    def parse(self, data, raw=True):
        if raw:
            data = self._parser.parseString(data)
        if not data:
            return None
        block_objects = []
        for block in data:
            block_type = block[0]
            kind_class = self._get_kind(block_type)
            params = {}
            for param in block[1:]:
                param_count = len(param)
                if not param_count:
                    _logger.warning(f'Empty param in block: {block}')
                    continue
                param_name = param[0][1:]
                if param_count == 1:
                    params[param_name] = True
                elif param_count == 2:
                    params[param_name] = param[1]
                elif param_count > 2:
                    params[param_name] = param[1:]
            block_object = kind_class(**params)
            block_objects.append(block_object)
        return block_objects

    def parse_file(self, filepath):
        data = self._parser.parseFile(filepath)
        return self.parse(data, raw=False)
