import logging
import re
from abc import ABC

from lib.utilities.logging import VerbosityLevel, ExitCode
from lib.utilities.logging.consts import VERBOSITY_LOGGER_NAME, \
    COLOR_EXTRA_KEYWORD, VERBOSITY_COLOR


class WithLogging(ABC):
    def __init__(self):
        self._logger = logging.getLogger(
            f'{VERBOSITY_LOGGER_NAME}.{self._normalized_name()}')
        self._logger.setLevel(logging.DEBUG)

    def _normalized_name(self):
        def repl(match):
            g1 = match.group(1)
            s = '-' if g1 == '_' else (f'{g1}_' if g1 else '')
            return s + match.group(2).lower()

        return re.sub(r'([a-z0-9_]|^)([A-Z])', repl, self.__class__.__name__)

    def _verbose(self, level: VerbosityLevel, message: str, arg=None, header=None):
        if header:
            message = f'{header} : {message}'
        if arg:
            message = f'{message}:\n\t{arg!s}'.expandtabs(4)
        self._logger.log(level.value,
                         message,
                         extra={COLOR_EXTRA_KEYWORD: VERBOSITY_COLOR[level]})

    def _critical(self, message: str, exit_code: ExitCode, arg=None, header=None):
        """
        This method is used when a critical error is found.
        It just log the error and exit the application with the given exit_code
        """
        self._verbose(VerbosityLevel.CRITICAL, message, arg, header)
        logging.shutdown()
        exit(exit_code.value)

    def _error(self, message: str = '', arg=None, header=None):
        self._verbose(VerbosityLevel.ERROR, message, arg, header)

    def _warning(self, message: str = '', arg=None, header=None):
        self._verbose(VerbosityLevel.WARNING, message, arg, header)

    def _info(self, message: str = '', arg=None, header=None):
        self._verbose(VerbosityLevel.INFO, message, arg, header)

    def _debug(self, message: str = '', arg=None, header=None):
        self._verbose(VerbosityLevel.DEBUG, message, arg, header)
