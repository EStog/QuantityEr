import logging
from typing import TextIO, Iterable, Tuple

from lib.utilities.enums import VerbosityLevel
from lib.config.consts import OUTPUT_LOGGER_NAME, VERBOSITY_LOGGER_NAME, \
    CONSOLE_OUTPUT_FORMAT, FILE_OUTPUT_FORMAT


def config_loggers(silent: bool, console_verbosity: VerbosityLevel,
                   log_files: Iterable[Tuple[VerbosityLevel, TextIO]]):
    output_logger = logging.getLogger(OUTPUT_LOGGER_NAME)
    output_logger.setLevel(logging.DEBUG)
    verbosity_logger = logging.getLogger(VERBOSITY_LOGGER_NAME)
    verbosity_logger.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter(
        CONSOLE_OUTPUT_FORMAT,
        style='{')
    file_formatter = logging.Formatter(
        FILE_OUTPUT_FORMAT,
        style='{')
    if not silent:
        console_output_handler = logging.StreamHandler()
        console_output_handler.setFormatter(console_formatter)
        output_logger.addHandler(console_output_handler)
    if console_verbosity:
        console_verbosity_handler = logging.StreamHandler()
        console_verbosity_handler.setLevel(console_verbosity.value.upper())
        console_verbosity_handler.setFormatter(console_formatter)
        verbosity_logger.addHandler(console_verbosity_handler)
    for verbosity_level, file in log_files:
        handler = logging.StreamHandler(file)
        handler.setFormatter(file_formatter)
        handler.setLevel(verbosity_level.value.upper())
        verbosity_logger.addHandler(handler)
