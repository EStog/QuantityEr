import re
import argparse
import logging
from logging import Logger
from typing import Iterable, Tuple, Type

from lib.config.consts import VERBOSITY_LOGGER_NAME, COLOR, COLOR_EXTRA_KEYWORD, OUTPUT_LOGGER_NAME
from lib.utilities.enums import ExitCode, VerbosityLevel


def critical_error(message: str, exitcode: ExitCode,
                   logger: Logger = logging.getLogger(VERBOSITY_LOGGER_NAME), error=None):
    verbose_output(VerbosityLevel.CRITICAL, message, logger, error)
    logging.shutdown()
    exit(exitcode.value)


def get_verbosity_file_caster():
    def verbosity_file(a):
        if verbosity_file.verbosity:
            cast_function = VerbosityLevel
            verbosity_file.__name__ = VerbosityLevel.__name__
        else:
            file_caster = argparse.FileType('w')
            cast_function = file_caster
        verbosity_file.verbosity = not verbosity_file.verbosity
        return cast_function(a)

    verbosity_file.verbosity = True
    return verbosity_file


def cast_tuple_from_str(values: Iterable[object], cast_funcs: Iterable[type]) -> \
        Tuple[object, ...]:
    result = ()
    for value, cast_func in zip(values, cast_funcs):
        if isinstance(value, str):
            result += (cast_from_str(value, cast_func),)
        else:
            result += (value,)
    return result


def cast_from_str(value: str, cast_func: type) -> object:
    try:
        casted_value = cast_func(value)
    except ValueError as e:
        critical_error(f'Error while casting {value} to {cast_func}',
                       ExitCode.TYPING, error=e)
    else:
        return casted_value


def output(message: str, logger: Logger = logging.getLogger(OUTPUT_LOGGER_NAME),
           extra=None):
    if extra is not None:
        message = f'{message}:\n\t{extra!s}'
    logger.info(message, extra={COLOR_EXTRA_KEYWORD: COLOR[VerbosityLevel.INFO]})


def verbose_output(severity: VerbosityLevel, message: str,
                   logger: Logger = logging.getLogger(VERBOSITY_LOGGER_NAME),
                   extra=None):
    if extra is not None:
        message = f'{message}:\n\t{extra!s}'
    logger.log(getattr(logging, severity.value.upper()),
               message,
               extra={COLOR_EXTRA_KEYWORD: COLOR[severity]})


def get_instance(ttype: Type, kwargs: dict):
    try:
        obj = ttype(**kwargs)
    except TypeError as e:
        critical_error(f'Error while creating instance of {ttype.__name__}', ExitCode.TYPING, error=e)
    else:
        return obj


def normalize_name(name):
    def repl(match):
        g1 = match.group(1)
        s = '-' if g1 == '_' else (f'{g1} ' if g1 else '')
        return s + match.group(2).lower()

    return re.sub(r'([a-z0-9_]|^)([A-Z])', repl, name)


def cast_to_verbosity_level_or_none(level):
    if level == 'None':
        return None
    else:
        return VerbosityLevel(level)


__all__ = ['critical_error', 'get_verbosity_file_caster',
           'output', 'verbose_output', 'cast_tuple_from_str',
           'get_instance', 'normalize_name']
