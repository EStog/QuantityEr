import logging
from abc import ABCMeta

from lib.utilities.enums import ExitCode
from lib.utilities.enums import VerbosityLevel
from lib.utilities.functions import verbose_output, critical_error


class WithDefaults(metaclass=ABCMeta):
    """This class manage its defaults in a way that can be presented to the outside"""

    DEFAULTS_DICT = {}

    def __init__(self, **kwargs):
        """Initializes the arguments that are None if a default value has been given.
        Otherwise the value remains None"""
        self._set_attributes(**kwargs)
        from lib.config.consts import VERBOSITY_LOGGER_NAME
        self._logger = logging.getLogger(f'{VERBOSITY_LOGGER_NAME}.{self.__class__.__name__}')
        self._logger.setLevel(logging.DEBUG)

    def _set_attributes(self, **kwargs):
        for key in kwargs:
            setattr(self, f'_{key}', self._get_value(key, kwargs[key]))

    def _get_value(self, key: str, value) -> object:
        return self.DEFAULTS_DICT[key] if value is None and key in self.DEFAULTS_DICT else value

    def _verbose_output(self, level: VerbosityLevel, message: str, extra=None):
        verbose_output(level, message, self._logger, extra)

    def _critical_error(self, message: str, exit_code: ExitCode, error=None):
        critical_error(message, exit_code, self._logger, error)


__all__ = ['WithDefaults']
