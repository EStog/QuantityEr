import logging
from enum import Enum, unique


class XEnum(Enum):

    @property
    def name(self):
        return self._name_.lower()

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    @classmethod
    def cast_from_name(cls, name: str):
        name = name.upper()
        if name in cls.__members__:
            return cls.__members__[name]
        else:
            raise TypeError(f'{name} is not member of {cls.__name__}')

    @classmethod
    def default(cls):
        if 'DEFAULT' in cls.__members__:
            return cls.DEFAULT.name
        else:
            raise KeyError(f'Enum {cls.__name__} has no default')


class VerbosityLevel(XEnum):
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    DEFAULT = CRITICAL

    @classmethod
    def sorted_values_string(cls) -> str:
        s = ''
        for verbose_level in sorted(cls, key=lambda t: t.value, reverse=True):
            s += f'{verbose_level.value}, '
        return s[:-2]


@unique
class ExitCode(Enum):
    NORMAL = 0
    PARSING = 3
    ENGINE = 4
    TYPING = 5
    CONNECTION = 6
    QUERY_ERROR = 7
    FILE_ERROR = 8


__all__ = ['XEnum', 'VerbosityLevel', 'ExitCode']
