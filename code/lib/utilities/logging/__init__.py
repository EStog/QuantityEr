import logging
from enum import unique, Enum

from lib.utilities.xenum import XEnum


class VerbosityLevel(XEnum):
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    DEFAULT = INFO

    @classmethod
    def sorted_names_string(cls) -> str:
        s = ''
        # noinspection PyTypeChecker
        for verbose_level in sorted(cls, key=lambda t: t.value, reverse=True):
            s += f'{verbose_level.name}, '
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
