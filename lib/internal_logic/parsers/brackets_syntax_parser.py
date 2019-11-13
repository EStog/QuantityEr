import string
from typing import Mapping

from lib.internal_logic.parsers.parser import Parser
from lib.utilities.bi_dict import BiDict
from lib.utilities.classes import Argument
from lib.utilities.functions import normalize_name


class BracketsSyntaxParser(Parser):
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

    def _init_parameters(self):
        self._allow_redefine_ids = Argument(type=bool, default=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._names = {}
        self._literals_table = BiDict()

    @property
    def symbols_table(self) -> Mapping[str, str]:
        return self._literals_table

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
        if nm in self._names and not self._allow_redefine_ids:
            self._critical_error(code, f'Identifier "{nm}" has been already defined')
        sub_exp = self._parse_expression(code, '')
        self._names[nm] = sub_exp
        exp += f' {sub_exp}'
        return exp

    def _parse_expression_reference(self, code: Parser.Code, exp: str) -> str:
        code.next()
        nm = self._match_id(code)
        if nm not in self._names:
            self._critical_error(code, f'Identifier "{nm}" has not been defined before')
        exp += f' {self._names[nm]}'
        return exp

    def _parse_literal(self, code: Parser.Code, exp: str) -> str:
        literal = self._match_literal(code)
        if literal not in self._literals_table.sym:
            self._literals_table[f'v{len(self._literals_table)}'] = literal
        exp += f' {self._literals_table.sym[literal]}'
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


BracketsSyntaxParser.__name__ = normalize_name(BracketsSyntaxParser.__name__)

__all__ = ['BracketsSyntaxParser']
