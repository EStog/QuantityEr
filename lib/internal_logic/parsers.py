import string
from abc import abstractmethod
from typing import TextIO

from sympy import SympifyError, simplify_logic
from sympy.logic.boolalg import to_dnf

from lib.config.consts import QUERY_NAME_FORMAT, COMMANDLINE_NAME, QUOTE_FORMAT
from lib.utilities.classes import WithDefaults, Firm
from lib.utilities.enums import XEnum, ExitCode, VerbosityLevel
from lib.utilities.flip_dict import Flipdict
from lib.utilities.functions import critical_error, normalize_name


class Parser(WithDefaults):
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
        self.names = {}
        self.associations = Flipdict()

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
                       ExitCode.PARSING, self._logger, error)


class Brackets_SyntaxParser(Parser):
    """
    This parser implements the following grammar:

    <expression>             ::=  <conjunction>             |
                                  <disjunction>             |
                                  <negation>                |
                                  <named_expression>        |
                                  EXPRESSION_REFERENCE      |
                                  LITERAL
    <conjunction>            ::=  CONJUNCTION_INIT <expression> <expression> <expression_list> CONJUNCTION_END
    <disjunction>            ::=  DISJUNCTION_INIT <expression> <expression> <expression_list> DISJUNCTION_END
    <negation>               ::=  NEGATION_OP <expression>
    <named_expression>       ::=  REFERENT_DEFINITION <expression>
    <expression_list>        ::=  <expression> <expression_list> | empty_string

    An named expression is defined as something like this @<id> <expression>.
    The name must be an common identifier.

    A literal may not have whitespace characters, parenthesis or the initials of
    other rules.
    If some of this characters are desired inside a literal then quotes must be used as delimiters.
    Note that the kind of quotes you use as delimiters may not be inside the literal.

    A reference to a named expression is in the form $<id>.
    """

    REF_DEF_INIT = "@"
    EXP_REF_INIT = "$"
    CONJUNCTION_INIT = '['
    CONJUNCTION_END = ']'
    DISJUNCTION_INIT = '{'
    DISJUNCTION_END = '}'
    NEGATION_OP = "~"

    class _KW(XEnum):
        ALLOW_REDEFINE_IDS = Firm(bool, True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _parse_expression(self, code: Parser.Code, exp: str) -> str:
        """
        <expression>             ::=  <conjunction>             |
                                      <disjunction>             |
                                      <negation>                |
                                      <named_expression>        |
                                      EXPRESSION_REFERENCE      |
                                      LITERAL
        """

        code.consume_leading_spaces()
        if code.current_char == self.CONJUNCTION_INIT:
            return self._parse_group(code, exp, is_conjunction=True)
        elif code.current_char == self.DISJUNCTION_INIT:
            return self._parse_group(code, exp, is_conjunction=False)
        elif code.current_char == self.NEGATION_OP:
            return self._parse_negation(code, exp)
        elif code.current_char == self.REF_DEF_INIT:
            return self._parse_named_expression(code, exp)
        elif code.current_char == self.EXP_REF_INIT:
            return self._parse_expression_reference(code, exp)
        else:
            return self._parse_literal(code, exp)

    def _parse_group(self, code: Parser.Code, exp: str, is_conjunction: bool) -> str:
        """
        <conjunction> ::= CONJUNCTION_INIT <expression> <expression> <expression_list> CONJUNCTION_END
        <disjunction> ::= DISJUNCTION_INIT <expression> <expression> <expression_list> DISJUNCTION_END
        """
        code.next()
        exp += ' ('
        exp = self._parse_expression(code, exp)
        exp += ' &' if is_conjunction else ' |'
        exp = self._parse_expression(code, exp)
        exp = self._parse_expression_list(code, exp, is_conjunction)
        code.consume_leading_spaces()
        if code.current_char == (self.CONJUNCTION_END if is_conjunction else self.DISJUNCTION_END):
            exp += ')'
            code.next()
        else:
            self._critical_error(code, f"'{self.CONJUNCTION_END if is_conjunction else self.DISJUNCTION_END}' "
                                       "expected")
        return exp

    def _parse_expression_list(self, code: Parser.Code, exp: str,
                               is_conjunction: bool) -> str:
        """<expression_list> ::= <expression> <expression_list> | empty_string"""
        code.consume_leading_spaces()
        while code.current_char != (self.CONJUNCTION_END if is_conjunction else self.DISJUNCTION_END):
            exp += ' &' if is_conjunction else ' |'
            exp = self._parse_expression(code, exp)
            code.consume_leading_spaces()
        return exp

    def _parse_negation(self, code: Parser.Code, exp: str) -> str:
        """<negation> ::= NEGATION_OP <expression>"""
        exp += ' ~'
        code.next()
        return self._parse_expression(code, exp)

    def _parse_named_expression(self, code: Parser.Code, exp: str) -> str:
        """<named_expression> ::=  REFERENT_DEFINITION <expression>"""
        code.next()
        nm = self._match_id(code)
        if nm in self.names and not self._get(self._KW.ALLOW_REDEFINE_IDS):
            self._critical_error(code, f'Identifier "{nm}" has been already defined')
        sub_exp = self._parse_expression(code, '')
        self.names[nm] = sub_exp
        exp += f' {sub_exp}'
        return exp

    def _parse_expression_reference(self, code: Parser.Code, exp: str) -> str:
        code.next()
        nm = self._match_id(code)
        if nm not in self.names:
            self._critical_error(code, f'Identifier "{nm}" has not been defined before')
        exp += f' {self.names[nm]}'
        return exp

    def _parse_literal(self, code: Parser.Code, exp: str) -> str:
        literal = self._match_literal(code)
        if literal not in self.associations.flip:
            self.associations[f'v{len(self.associations)}'] = literal
        exp += f' {self.associations.flip[literal]}'
        return exp

    def _match_id(self, code: Parser.Code) -> str:
        """
        ID = r"[a-zA-Z_][a-zA-Z0-9_]*"
        """
        id_name = ''
        alfa = string.ascii_letters + '_'
        if code.current_char not in alfa:
            self._critical_error(code, "Identifier expected")
        else:
            id_name += code.current_char
            code.next()
            alfanum = alfa + string.digits
            while code.current_char in alfanum:
                id_name += code.current_char
                code.next()
        return id_name

    def _match_literal(self, code):
        """
        LITERAL =
            f'[^{NEGATION_OP}{REF_DEF_INIT}{EXP_REF_INIT}\\{CONJUNCTION_INIT}'
            f'\\{CONJUNCTION_END}{DISJUNCTION_INIT}{DISJUNCTION_END}\\"\\s]+|\\".+?\\"'
        """
        initials_finals = (self.NEGATION_OP + self.REF_DEF_INIT +
                           self.EXP_REF_INIT + self.CONJUNCTION_INIT +
                           self.CONJUNCTION_END + self.DISJUNCTION_INIT +
                           self.DISJUNCTION_END)
        literal = ''
        if code.current_char != '"':
            is_string = False
            if code.current_char in initials_finals:
                self._critical_error(code, 'Match with literal expected')
        else:
            is_string = True
        literal += code.current_char
        code.next()
        invalid_chars = initials_finals + '"' + string.whitespace
        while code.current_char not in invalid_chars:
            literal += code.current_char
            code.next()
        if is_string:
            if code.current_char != '"':
                self._critical_error(code, '" expected')
            else:
                literal += code.current_char
                code.next()
        return literal


Brackets_SyntaxParser.__name__ = normalize_name(Brackets_SyntaxParser.__name__)


class SyntaxType(XEnum):
    BRACKETS = Brackets_SyntaxParser
    DEFAULT = BRACKETS


__all__ = ['Parser', 'SyntaxType']
