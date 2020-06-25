from dataclasses import dataclass
from typing import Dict

from doiter_bfo.model import CrontabModel
from doiter_bfo.operations import decorator_cls
from doiter_bfo.operations.pyinfra import Pyinfra

from pyinfra.modules import server


@decorator_cls
@dataclass
class Crontab(CrontabModel):
    def _get_response(self) -> Dict:
        return {
            'name': self.name,
            'minute': self.minute,
            'hour': self.hour,
            'month': self.month,
            'day_of_month': self.day_of_month,
            'day_of_week': self.day_of_week,
            'command': self.command,
        }

    def _apply_pyinfra(self, pyinfra: Pyinfra, *args, **kwargs) -> Dict:
        """
        Add action to PyInfra object
        """
        params = {**self.__dict__}

        del params['command']

        response = self._get_response()

        response = pyinfra.add_action(
            action=server.crontab,
            desc=f'Add crontab {self.name}',
            response=response,
            args=[self.command],
            kwargs=params
        )

        return response

    def _apply_manual(self, *args, **kwargs) -> Dict:
        """
        Apply required action
        """

        raise NotImplementedError
