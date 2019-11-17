from abc import abstractmethod
from io import StringIO
from typing import TextIO, Iterable, Sequence, Union

from lib.classes import WithLoggingAndExternalArguments
from lib.classes.internal.middle_codes.middle_code import MiddleCode
from lib.utilities.functions import quote
from lib.utilities.logging import ExitCode, VerbosityLevel


class SourceCode:
    def __init__(self, source: Union[str, TextIO], namespace: str):
        if isinstance(source, str):
            self.__stream = StringIO(source)
        else:
            self.__stream = source
        self._namespace = namespace
        self._current_query_number = 0
        self._current_pos = 0
        self._current_line = 1
        self._current_char = ''
        self._current_query = ''
        self.next()

    def get_namespace_query_number(self):
        return self._namespace, self._current_query_number

    def next(self):
        self._current_char = self.__stream.read(1)
        self._current_query += self._current_char
        self._current_pos += 1
        if self._current_char == '\n':
            self._current_line += 1
            self._current_pos = 0

    def consume_leading_spaces(self):
        while self._current_char.isspace():
            self.next()

    def reset_current_query(self):
        self._current_query_number += 1
        self._current_query = self._current_char

    @property
    def current_char(self):
        return self._current_char

    @property
    def current_pos(self):
        return self._current_pos

    @property
    def current_line(self):
        return self._current_line

    @property
    def current_query(self):
        return self._current_query


class Parser(WithLoggingAndExternalArguments):
    """Abstract base class for parser"""

    def __init__(self, args_sequence: Sequence[str]):
        WithLoggingAndExternalArguments.__init__(self, args_sequence)
        self._middle_code_type = None
        self._only_one_query = False
        self._source_code = None
        self._middle_code = None

    def set_only_one_query(self):
        self._only_one_query = True

    def reset_only_one_query(self):
        self._only_one_query = False

    def get_middle_codes(self, source: Union[str, TextIO], namespace: str) -> Iterable[MiddleCode]:
        self._source_code = SourceCode(source, namespace)
        self._source_code.consume_leading_spaces()
        while self._source_code.current_char:
            middle_code = self.parse()
            if self._source_code.current_char and not self._source_code.current_char.isspace():
                self._parsing_critical(f'Extra characters in query {quote(middle_code.full_name)}')
            self._source_code.consume_leading_spaces()
            if self._only_one_query and self._source_code.current_char:
                self._parsing_critical(f'Extra characters in the query {quote(middle_code.full_name)}')
            yield middle_code

    def parse(self) -> MiddleCode:
        self._source_code.reset_current_query()
        self._middle_code = self._middle_code_type(*self._source_code.get_namespace_query_number())
        self._debug(f'Parsing ...')
        middle_code = self._parse(self._middle_code)
        self._debug(f'Query parsed')
        middle_code.original_query = self._source_code.current_query.strip()
        return middle_code

    @abstractmethod
    def _parse(self, middle_code: MiddleCode) -> MiddleCode:
        pass

    def _verbose(self, level: VerbosityLevel, message: str = '', arg=None, header=None):
        WithLoggingAndExternalArguments._verbose(self, level,
                                                 f'In position {self._source_code.current_line}:'
                                                 f'{self._source_code.current_pos}: {message}',
                                                 arg, self._middle_code.full_name)

    def _parsing_critical(self, message: str = '', arg=None):
        self._critical(message, ExitCode.PARSING, arg)
