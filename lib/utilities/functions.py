import datetime
import logging
import random
import re
from logging import Logger
from pathlib import Path
from typing import Iterable, Tuple, Type

from lib.config.consts import VERBOSITY_LOGGER_NAME, COLOR, COLOR_EXTRA_KEYWORD, OUTPUT_LOGGER_NAME
from lib.utilities.enums import ExitCode, VerbosityLevel


def critical_error(message: str, exitcode: ExitCode, error=None,
                   logger: Logger = logging.getLogger(VERBOSITY_LOGGER_NAME)):
    verbose_output(VerbosityLevel.CRITICAL, message, error, logger)
    logging.shutdown()
    exit(exitcode.value)


def get_tuple_caster(*casters):
    def func(a):
        caster = casters[func.i]
        try:
            func.__name__ = caster.__name__
        except AttributeError:
            pass
        func.i += 1
        if func.i == len(casters):
            func.i = 0
        return caster(a)

    func.i = 0
    return func


def get_time_prognostic(n: int, delay: int, waiting_factor: int) -> Tuple[str, str]:
    return (str(datetime.timedelta(seconds=n * delay)),
            str(datetime.timedelta(seconds=n * delay * waiting_factor)))


def get_waiting_time(timeout: int, waiting_factor: int):
    return random.randint(timeout, timeout * waiting_factor) + random.random()


def get_included_excluded_principle_iter_amount(n: int):
    r = 0
    for p in range(1, n + 1):
        r += combination_amount(n, p)
    return r


def combination_amount(n: int, p: int) -> int:
    n_p = n - p
    numerator_init = max(p, n_p)
    denominator_end = min(p, n_p)
    num = 1
    for i in range(numerator_init + 1, n + 1):
        num *= i
    den = 1
    for i in range(1, denominator_end + 1):
        den *= i
    return num // den


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


def verbose_output(severity: VerbosityLevel, message: str, extra=None,
                   logger: Logger = logging.getLogger(VERBOSITY_LOGGER_NAME)):
    if extra is not None:
        message = f'{message}:\n\t{extra!s}'.expandtabs(4)
    logger.log(severity.value,
               message,
               extra={COLOR_EXTRA_KEYWORD: COLOR[severity]})


def output(message: str, extra=None, logger: Logger = logging.getLogger(OUTPUT_LOGGER_NAME)):
    if extra is not None:
        message = f'{message}:\n\t{extra!s}'.expandtabs(4)
    logger.info(message, extra={COLOR_EXTRA_KEYWORD: COLOR[VerbosityLevel.INFO]})


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


def get_caster_to_optional(ttype):
    def f(value: str):
        if not value:
            return value
        else:
            return ttype(value)

    return f


def div(a: int, b: int):
    return a / b if b != 0 else 0


def create_path(path: Path):
    """
    Returns True if path is a file, else returns False.
    Creates the path if it does not exists
    """
    if not path.exists():
        try:
            path.touch()
            return True
        except FileNotFoundError:
            try:
                path.mkdir(parents=True)
                return False
            except OSError as e:
                critical_error(f'Cannot create directory {path} for output',
                               ExitCode.FILE_ERROR, error=e)
    else:
        return path.is_file()


def open_file(path: Path, mode: str):
    try:
        file = path.open(mode)
    except OSError as e:
        critical_error(f'Cannot open file {path.name}', ExitCode.FILE_ERROR, error=e)
    else:
        return file

__all__ = ['critical_error', 'get_tuple_caster',
           'output', 'verbose_output', 'cast_tuple_from_str',
           'get_instance', 'normalize_name', 'div',
           'get_included_excluded_principle_iter_amount',
           'get_caster_to_optional', 'create_path',
           'get_waiting_time', 'get_time_prognostic']
