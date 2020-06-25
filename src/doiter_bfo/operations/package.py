import subprocess
import shlex
from dataclasses import dataclass
from typing import Dict

from doiter_bfo.model import PackageModel
from doiter_bfo.operations import decorator_cls
from doiter_bfo.operations.pyinfra import Pyinfra

from pyinfra.modules import yum


@decorator_cls
@dataclass
class Package(PackageModel):
    pkg_manager: str = 'yum'

    def _get_response(self) -> Dict:
        return {
            'package': self.name,
            'state': 'present' if self.installed else 'absent',
            'stdout': None,
            'stderr': None,
            'exit_code': None,
        }

    def _apply_pyinfra(self, pyinfra: Pyinfra, *args, **kwargs) -> Dict:
        """
        Add action to PyInfra object
        """
        params = {
            'latest': True,
            'update': False,
            'present': True,
        }
        if not self.installed:
            params['present'] = False

        response = self._get_response()

        response = pyinfra.add_action(
            action=yum.packages,
            desc=f'Install {self.name}',
            response=response,
            args=[self.name],
            kwargs=params
        )

        return response

    def _apply_manual(self, *args, **kwargs) -> Dict:
        """
        Apply required action
        """

        command_args = shlex.split('install -y')
        if not self.installed:
            command_args = shlex.split('erase -y')

        command = ' '.join([self.pkg_manager] + command_args + [self.name])

        process = subprocess.Popen(command, executable='/bin/bash', shell=True,
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
