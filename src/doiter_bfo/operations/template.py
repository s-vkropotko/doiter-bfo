import shutil
import os
import tempfile
import hashlib
from dataclasses import dataclass
from typing import Dict

from doiter_bfo.model import TemplateModel
from doiter_bfo.operations import decorator_cls
from doiter_bfo.operations.pyinfra import Pyinfra

from pyinfra.modules import files

TEMP_DIRECTORY = tempfile.TemporaryDirectory()


@decorator_cls
@dataclass
class Template(TemplateModel):
    def _manage_dir(self, response):
        if not self.exists:
            if self.dest not in ['.', '/', '/*'] and '*' not in self.dest:
                shutil.rmtree(self.dest)
            elif self.force:
                shutil.rmtree(self.dest)
            else:
                response['operation'] = 'failed'
                response['description'] = 'To destroy directory with this patter "force" \
                flag is required'
                return response
        else:
            os.mkdir(self.dest)
        response['operation'] = 'success'
        return response

    def _get_response(self) -> Dict:
        return {
            'name': self.name,
            'src': self.src,
            'dest': self.dest,
            'description': '',
            'exists': self.exists
        }

    def _apply_pyinfra(self, pyinfra: Pyinfra, *args, **kwargs) -> Dict:
        params = {
            'user': self.user,
            'group': self.group,
            'sudo': self.sudo
        }

        response = self._get_response()

        if self.directory:
            params['recursive'] = True
            params['present'] = self.exists
            response = pyinfra.add_action(
                action=files.directory,
                desc=f'Directory {self.name} dest path: {self.dest}',
                response=response,
                kwargs=params
            )
        else:
            if self.content:
                # Hack -> TODO
                temp_directory = TEMP_DIRECTORY
                file_hash = hashlib.md5(self.content.encode()).hexdigest()
                file_path = os.path.join(temp_directory.name, file_hash)
                temporary_file = open(file_path, 'w')
                temporary_file.write(self.content)
                temporary_file.close()
                self.src = file_path

            params['create_remote_dir'] = True

            if self.template:
                params['template_filename'] = self.src
                params['remote_filename'] = self.dest
                response = pyinfra.add_action(
                    action=files.template,
                    desc=f'File {self.name} dest path: {self.dest}',
                    response=response,
                    kwargs=params
                )
            else:
                params['local_filename'] = self.src
                params['remote_filename'] = self.dest
                response = pyinfra.add_action(
                    action=files.put,
                    desc=f'File {self.name} dest path: {self.dest}',
                    response=response,
                    kwargs=params
                )

        return response

    def _apply_manual(self, *args, **kwargs) -> Dict:
        """
        Apply required action
        """
        response = self._get_response()

        if self.directory:
            return self._manage_dir(response)

        if self.exists:
            with open(self.dest, 'w') as f:
                f.write(self.content)
        else:
            os.remove(self.dest)
        response['operation'] = 'success'

        return response
