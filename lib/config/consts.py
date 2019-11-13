"""
This sets general parameters to be used in the application.
Don't modify at least you know what you what you are doing
"""

import colorama
from colorama import Style

from lib.utilities.enums import VerbosityLevel

APPLICATION_NAME = 'AmountEr'
APPLICATION_VERSION = '0.9'
APPLICATION_NAME_VERSION = f'{APPLICATION_NAME} {APPLICATION_VERSION}'

OUTPUT_LOGGER_NAME = f'output'
VERBOSITY_LOGGER_NAME = f'verbose'
COLOR_EXTRA_KEYWORD = 'color_init'
CONSOLE_OUTPUT_FORMAT = (f'{Style.DIM}'
                         '{asctime} : {name} : '
                         f'{Style.RESET_ALL}'
                         f'{{{COLOR_EXTRA_KEYWORD}}}'
                         '{message}'
                         f'{Style.RESET_ALL}')
FILE_OUTPUT_FORMAT = ('{asctime} : {name} : '
                      '{levelname} : {message}')
COMMANDLINE_NAME = 'CONSOLE'
QUERY_NAME_FORMAT = '{query_namespace}.{i}'
QUOTE_FORMAT = '<{}>'
SUBQUERY_NAME_FORMAT = '{query_name}.{i}'
OUTPUT_FILE_EXT = 'out'
INPUT_FILE_EXT = 'in'
SIMULATION_TAG = 'simulation'
OUTPUT_FILE_FORMAT = f'{{name}}.{OUTPUT_FILE_EXT}'
OUTPUT_SIMULATION_FILE_FORMAT = f'{{name}}-{SIMULATION_TAG}.{OUTPUT_FILE_EXT}'

COLOR = {
    VerbosityLevel.INFO: colorama.Fore.GREEN,
    VerbosityLevel.CRITICAL: colorama.Fore.RED + colorama.Style.BRIGHT,
    VerbosityLevel.WARNING: colorama.Fore.YELLOW,
    VerbosityLevel.DEBUG: colorama.Style.DIM,
    VerbosityLevel.ERROR: colorama.Fore.RED
}

__all__ = ['APPLICATION_NAME_VERSION',
           'OUTPUT_LOGGER_NAME', 'VERBOSITY_LOGGER_NAME',
           'CONSOLE_OUTPUT_FORMAT', 'FILE_OUTPUT_FORMAT',
           'COLOR', 'COLOR_EXTRA_KEYWORD',
           'COMMANDLINE_NAME', 'QUERY_NAME_FORMAT',
           'OUTPUT_FILE_EXT', 'QUOTE_FORMAT',
           'SUBQUERY_NAME_FORMAT']
