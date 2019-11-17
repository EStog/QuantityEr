from typing import Iterable, Sequence

from lib.classes.inputs.input import Input
from lib.classes.internal.middle_codes.middle_code import MiddleCode
from lib.utilities.with_external_arguments import CustomArgumentParser


class StrInput(Input):
    COMMANDLINE_NAME = 'CONSOLE'

    def __init__(self, source: Iterable[str],
                 parser_options: Sequence[str],
                 main_args_parser: CustomArgumentParser):
        Input.__init__(self, source, parser_options, main_args_parser)
        complete_source = ''
        for source in self._source:
            complete_source += f'{source} '
        self._source = complete_source

    def get_middle_codes(self) -> Iterable[MiddleCode]:
        for middle_code in self._parser.get_middle_codes(self._source, self.COMMANDLINE_NAME):
            yield middle_code
