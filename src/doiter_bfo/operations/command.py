import subprocess
import shlex
from dataclasses import dataclass
from typing import Dict

from doiter_bfo.model import CommandModel
from doiter_bfo.operations import decorator_cls
from doiter_bfo.operations.pyinfra import Pyinfra

from pyinfra.modules import server


@decorator_cls
@dataclass
class Command(CommandModel):
    def _get_response(self) -> Dict:
        return {
            'name': self.name,
            'command': self.command,
            'stdout': None,
            'stderr': None,
            'exit_code': None,
        }

    def _apply_pyinfra(self, pyinfra: Pyinfra, *args, **kwargs) -> Dict:
        """
        Add action to PyInfra object
        """
        params = {}

        response = self._get_response()

        response = pyinfra.add_action(
            action=server.shell,
            desc=f'Run {self.name}',
            response=response,
            args=[self.command],
            kwargs=params
        )

        return response

    def _apply_manual(self, *args, **kwargs) -> Dict:
        """
        Apply required action
        """

        process = subprocess.Popen(self.command, executable='/bin/bash', shell=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        process.wait()

        response = self._get_response()

        response['stdout'] = process.stdout.readlines()
        response['stderr'] = process.stderr.readlines()
        response['exit_code'] = process.returncode

        if process.returncode == 0:
            response['operation'] = 'success'
        else:
            response['operation'] = 'failed'
        return response
