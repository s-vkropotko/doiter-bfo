import subprocess
from typing import Dict
from dataclasses import dataclass

from doiter_bfo.model import ServiceModel, State
from doiter_bfo.operations import decorator_cls
from doiter_bfo.operations.pyinfra import Pyinfra

from pyinfra.modules import init


@decorator_cls
@dataclass
class Service(ServiceModel):
    service_manager: str = 'systemctl'

    def _get_response(self) -> Dict:
        return {
            'service': self.name,
            'state': self.state,
            'description': '',
            'stdout': None,
            'stderr': None,
            'exit_code': None
        }

    def _apply_pyinfra(self, pyinfra: Pyinfra, *args, **kwargs) -> Dict:
        """
        Add action to PyInfra object
        """
        params = {
            #            'reloaded': True,
            'enabled': True,
            'running': True
        }

        response = self._get_response()

        if self.state is State.STOPPED:
            params['running'] = False
        elif self.state is State.RESTARTED:
            params['restarted'] = True
        elif self.state is State.UNKNOWN:
            return response

        response = pyinfra.add_action(
            action=init.systemd,
            desc=f'Service {self.name} desired state {self.state}',
            response=response,
            args=[self.name],
            kwargs=params
        )

        return response

    def _apply_manual(self, *args, **kwargs) -> Dict:
        """
        Apply required action
        """

        response = self._get_response()

        state_action = {
            State.STARTED: 'start',
            State.STOPPED: 'stop',
            State.RESTARTED: 'restart'
        }

        if self.state in state_action.keys():
            command_args = [state_action[self.state]]
        else:
            response['description'] = 'Unknown desired state'
            return response

        command = ' '.join([self.service_manager] + command_args + [self.name])

        process = subprocess.Popen(command, executable='/bin/bash', shell=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        process.wait()

        response['stdout'] = process.stdout.readlines()
        response['stderr'] = process.stderr.readlines()
        response['exit_code'] = process.returncode

        return response
