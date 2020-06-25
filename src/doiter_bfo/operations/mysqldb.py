from dataclasses import dataclass
from typing import Dict

from doiter_bfo.model import MysqlDBModel
from doiter_bfo.operations import decorator_cls
from doiter_bfo.operations.pyinfra import Pyinfra

from pyinfra.modules import mysql


@decorator_cls
@dataclass
class Mysqldb(MysqlDBModel):
    def _get_response(self) -> Dict:
        return {
            'mysql_database': self.name,
        }

    def _apply_pyinfra(self, pyinfra: Pyinfra, *args, **kwargs) -> Dict:
        """
        Add action to PyInfra object
        """
        params = {**self.__dict__}

        del params['name']

        response = self._get_response()

        response = pyinfra.add_action(
            action=mysql.database,
            desc=f'Add mysql db {self.name}',
            response=response,
            args=[self.name],
            kwargs=params
        )

        return response

    def _apply_manual(self, *args, **kwargs) -> Dict:
        """
        Apply required action
        """

        raise NotImplementedError
