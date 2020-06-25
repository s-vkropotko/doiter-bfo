from collections import defaultdict
from typing import Dict

from pyinfra.api import Config, Inventory, State
from pyinfra.api.connect import connect_all
from pyinfra.api.connectors.local import make_names_data as make_names_data_local
# from pyinfra.api.facts import get_facts
from pyinfra.api.operation import add_op
from pyinfra.api.operations import run_ops


class Pyinfra:
    """
    Class to summorize pyinfra api code
    """

    def __init__(self,
                 make_names_data=make_names_data_local,
                 general_facts={},
                 fail_percent=100,
                 connect_timeout=5,
                 ):
        hosts = []
        groups = defaultdict(lambda: ([], {}))

        names_data = make_names_data() if callable(
            make_names_data) else make_names_data

        for name, data, group_names in names_data:
            hosts.append((name, data))
            for group_name in group_names:
                if name not in groups[group_name][0]:
                    groups[group_name][0].append(name)

        for host in hosts:
            for fact_name, fact in general_facts.items():
                host[1][fact_name] = fact

        # First we setup some inventory we want to target
        # the first argument is a tuple of (list all all hosts, global/ALL data)
        self.inventory = Inventory((hosts, {}), **groups)

        # Now we create a new config (w/optional args)
        self.config = Config(
            FAIL_PERCENT=fail_percent,
            CONNECT_TIMEOUT=connect_timeout,
        )

        # Setup the pyinfra state for this deploy
        self.state = State(self.inventory, self.config)

    def connect_to_hosts(self):
        connect_all(self.state)

    def apply(self):
        run_ops(self.state)

    def add_action(self, action, desc: str, args: list = [], kwargs: dict = {},
                   response=None, apply=False) -> Dict:

        add_op(
            # self.state, yum.packages,
            self.state, action,
            {desc},
            *args,
            **kwargs
        )
        # TODO fullfil response after apply
        if apply:
            self.apply()
        return response
