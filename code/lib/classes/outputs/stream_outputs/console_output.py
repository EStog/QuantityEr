import sys
from typing import TextIO

import colorama

from lib.classes.internal.middle_codes.middle_code import MiddleCode
from lib.classes.outputs.stream_outputs.stream_output import StreamOutput


class ConsoleOutput(StreamOutput):

    def __init__(self):
        StreamOutput.__init__(self)

    def _get_message(self, *args, **kwargs) -> str:
        return (f'{colorama.Fore.GREEN}'
                f'{StreamOutput._get_message(self, *args, **kwargs)}'
                f'{colorama.Style.RESET_ALL}')

    def _get_stream(self, middle_code: MiddleCode, is_simulation: bool) -> TextIO:
        return sys.stdout
