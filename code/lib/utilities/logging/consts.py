import colorama

from lib.utilities.logging import VerbosityLevel

VERBOSITY_LOGGER_NAME = f'verbose'

COLOR_EXTRA_KEYWORD = 'color_init'
CONSOLE_OUTPUT_FORMAT = (f'{colorama.Style.DIM}'
                         '{asctime} : {name} : '
                         f'{colorama.Style.RESET_ALL}'
                         f'{{{COLOR_EXTRA_KEYWORD}}}'
                         '{message}'
                         f'{colorama.Style.RESET_ALL}')
FILE_OUTPUT_FORMAT = ('{asctime} : {name} : '
                      '{levelname} : {message}')

VERBOSITY_COLOR = {
    VerbosityLevel.INFO: colorama.Fore.GREEN,
    VerbosityLevel.CRITICAL: colorama.Fore.RED + colorama.Style.BRIGHT,
    VerbosityLevel.WARNING: colorama.Fore.YELLOW,
    VerbosityLevel.DEBUG: colorama.Style.DIM,
    VerbosityLevel.ERROR: colorama.Fore.RED
}
