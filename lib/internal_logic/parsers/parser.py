from abc import abstractmethod
from typing import TextIO, Mapping

from sympy import SympifyError, simplify_logic
from sympy.logic.boolalg import to_dnf

from lib.config.consts import QUERY_NAME_FORMAT, COMMANDLINE_NAME, QUOTE_FORMAT
from lib.utilities.classes import WithArguments
from lib.utilities.enums import ExitCode, VerbosityLevel
from lib.utilities.functions import critical_error


class Parser(WithArguments):
    """Abstract base class for parser"""

    class Code:
        def __init__(self, stream: TextIO):
            self.__stream = stream
            self.current_pos = 0
            self.current_line = 1
            self.current_char = ''
            self.next()

        def next(self):
            self.current_char = self.__stream.read(1)
            self.current_pos += 1
            if self.current_char == '\n':
                self.current_line += 1
                self.current_pos = 0

        def consume_leading_spaces(self):
            while self.current_char.isspace():
                self.next()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._query_namespace = COMMANDLINE_NAME
        self._current_query_number = 0

    @property
    @abstractmethod
    def symbols_table(self) -> Mapping[str, str]:
        pass

    def set_namespace(self, query_namespace: str):
        self._query_namespace = query_namespace
        self._current_query_number = 0

    def get_symbolic_expression(self, code: TextIO, only_one_query: bool = False) -> str:
        code = self.Code(code)
        code.consume_leading_spaces()
        while code.current_char:
            self._current_query_number += 1
            query_name = QUERY_NAME_FORMAT.format(
                query_namespace=self._query_namespace,
                i=self._current_query_number
            )
            self._verbose_output(VerbosityLevel.INFO, f'Parsing query {QUOTE_FORMAT.format(query_name)} ...')
            exp = self._parse_expression(code, '')
            self._verbose_output(VerbosityLevel.INFO, f'Query {QUOTE_FORMAT.format(query_name)} parsed')
            try:
                self._verbose_output(VerbosityLevel.DEBUG, f'Converting {QUOTE_FORMAT.format(query_name)} to DNF ...')
                exp = simplify_logic(exp)
                exp = str(to_dnf(exp))
                self._verbose_output(VerbosityLevel.DEBUG, f'Query {QUOTE_FORMAT.format(query_name)} converted to DNF')
                yield query_name, exp
            except SympifyError as e:
                self._critical_error(code,
                                     f'Can not convert to boolean expression query {QUOTE_FORMAT.format(query_name)}.\n'
                                     f'Sympify error', e)
            if not code.current_char.isspace():
                self._critical_error(code, f'Extra characters in query {QUOTE_FORMAT.format(query_name)}')
            code.consume_leading_spaces()
            if only_one_query and code.current_char:
                self._critical_error(code, f'Extra characters in the query {QUOTE_FORMAT.format(query_name)}')

    @abstractmethod
    def _parse_expression(self, code: Code, exp: str) -> str:
        """Parse an expression"""
        pass

    def _critical_error(self, code: Code, message: str, error=None):
        """This method is used when a critical error is found. It just log the error and exit the application"""
        critical_error(f'Parsing error in {code.current_line}:{code.current_pos}:\n\t{message}',
                       ExitCode.PARSING, error, self._logger)


__all__ = ['Parser']
