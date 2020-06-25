from dataclasses import dataclass
from enum import Enum, unique


class BFOException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'{self.__class__.__name__}, {self.message}'
        else:
            return f'{self.__class__.__name__} has been raised'


@dataclass
class BaseBlock:
    name: str


@dataclass
class PackageModel(BaseBlock):
    latest: bool = True
    present: bool = True
    update: bool = False
    sudo: bool = False


@unique
class State(str, Enum):
    STOPPED = 'stopped'
    STARTED = 'started'
    RESTARTED = 'restarted'
    UNKNOWN = 'unknown'

    def __repr__(self):
        return self.value


@dataclass
class ServiceModel(BaseBlock):
    state: State = State.UNKNOWN
    enabled: bool = True
    running: bool = True
    sudo: bool = False


@dataclass
class CommandModel(BaseBlock):
    command: str
    sudo: bool = False


@dataclass
class TemplateModel(BaseBlock):
    dest: str
    src: str = None
    content: str = None
    exists: bool = True
    directory: bool = False
    force: bool = False
    user: str = None
    group: str = None
    template: bool = False
    sudo: bool = False

    def __post_init__(self):
        if not any((self.src, self.content)):
            raise BFOException('one of src,content must be provided')


"""
TODO:
Better handling day_of_month and day_of_week
@unique
class WeekDay(str, Enum):
    Monday = 'monday'
    Tuesday = 'tuesday'
    Wednesday = 'wednesday'
    Thursday = 'thursday'
    Friday = 'friday'
    Saturday = 'saturday'
    Sunday = 'sunday'

    UNKNOWN = 'unknown'

    def __repr__(self):
        return self.value
"""


@dataclass
class CrontabModel(BaseBlock):
    minute: str = '0'
    hour: str = '*'
    month: str = '*'
    day_of_week: str = '*'
    day_of_month: str = '*'
    command: str = '*'
    present: bool = True
    sudo: bool = False
#    interpolate_variables: bool = True


@dataclass
class MysqlUserModel(BaseBlock):
    password: str = None
    privileges: str = None
    sudo: bool = False


@dataclass
class MysqlDBModel(BaseBlock):
    sudo: bool = False
