from enum import Enum, unique


class XEnum(Enum):

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.value


class VerbosityLevel(XEnum):
    CRITICAL = 'critical'
    ERROR = 'error'
    WARNING = 'warning'
    INFO = 'info'
    DEBUG = 'debug'
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
