from abc import abstractmethod
from typing import Iterable, Sequence

from lib.classes.internal.middle_codes.middle_code import MiddleCode
from lib.classes.internal.parsers import PARSER_TYPE
from lib.utilities.functions import get_component
from lib.utilities.logging.with_logging import WithLogging
from lib.utilities.with_external_arguments import CustomArgumentParser


class Input(WithLogging):

    def __init__(self, source, parser_options: Sequence[str],
                 main_args_parser: CustomArgumentParser):
        WithLogging.__init__(self)
        self._source = source
        self._parser = get_component(parser_options, PARSER_TYPE, 'parser',
                                     main_args_parser)

    @abstractmethod
    def get_middle_codes(self) -> Iterable[MiddleCode]:
        pass
