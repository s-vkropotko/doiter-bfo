from dataclasses import dataclass
from typing import Dict
from doiter_bfo.model import BFOException


@dataclass
class Inventory:
    name: str
    ip_address: str = None
    ssh_port: int = 22
    ssh_user: str = 'root'
    ssh_key: str = None
    ssh_password: str = None
    ssh_key_password: str = None

    def __post_init__(self):
        if not any((self.ssh_key, self.ssh_password)):
            raise BFOException('one of ssh_key/ssh_password must be provided')

    def get_connect_address(self) -> str:
        if self.ip_address:
            return self.ip_address
        return self.name

    def host_facts(self) -> Dict:
        facts = {}

        self_facts = self.__dict__
        del self_facts['name']

        for key, value in self_facts.items():
            if value:
                facts[key] = value
        return facts
