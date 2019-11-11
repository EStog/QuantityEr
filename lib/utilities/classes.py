import logging
from abc import ABCMeta
from typing import Union, Callable

from lib.utilities.enums import ExitCode, XEnum
from lib.utilities.enums import VerbosityLevel
from lib.utilities.functions import verbose_output, critical_error


class Firm:
    def __init__(self, ttype: Union[type, Callable[[str], object]],
                 default: object = None, optional: bool = True):
        self.ttype = ttype
        self.default = default
        self.optional = optional


class WithDefaults(metaclass=ABCMeta):
    """This class manage its defaults in a way that can be presented to the outside"""

    class _KW(XEnum):
        pass

    def get_defaults_info(self):
        pass

    def __init__(self, **kwargs):
        """Initializes the arguments that are None if a default value has been given.
        Otherwise the value remains None"""
        from lib.config.consts import VERBOSITY_LOGGER_NAME
        self._logger = logging.getLogger(f'{VERBOSITY_LOGGER_NAME}.{self.__class__.__name__}')
        self._logger.setLevel(logging.DEBUG)
        self._set_attributes(**kwargs)

    def _set_attributes(self, **kwargs):
        arg_firm = None
        for key in kwargs:
            try:
                arg_firm = self._KW.cast_from_name(key).value
            except TypeError:
                self._critical_error(f'{self.__class__.__name__} does not expect argument {key}',
                                     ExitCode.TYPING)

            value = kwargs[key]
            if isinstance(value, str):
                try:
                    kwargs[key] = arg_firm.ttype(value)
                except ValueError as e:
                    self._critical_error(f'Error while casting {value} to {arg_firm.ttpye}',
                                         ExitCode.TYPING, error=e)
            setattr(self, f'_{key}', self._get_value(arg_firm.default, kwargs[key]))
        for arg in self._KW:
            if arg.name not in kwargs:
                if not arg.value.optional:
                    self._critical_error(f'Need "{arg.name}" argument to create instance of {self.__class__.__name__}',
                                         ExitCode.TYPING)
                else:
                    self._set(arg, arg.value.default)

    def _get(self, arg: _KW):
        return getattr(self, f'_{arg.name}')

    def _set(self, arg: _KW, value):
        setattr(self, f'_{arg.name}', value)

    @staticmethod
    def _get_value(default, value):
        return default if value is None else value

    def _verbose_output(self, level: VerbosityLevel, message: str, extra=None):
        verbose_output(level, message, self._logger, extra)

    def _critical_error(self, message: str, exit_code: ExitCode, error=None):
        critical_error(message, exit_code, self._logger, error)


__all__ = ['WithDefaults', 'Firm']
