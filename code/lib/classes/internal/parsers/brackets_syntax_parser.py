import string
from typing import Dict, Sequence

import sympy

from lib.classes.internal.middle_codes.sympy_logic_middle_code import SympyLogicMiddleCode
from lib.classes.internal.parsers.parser import Parser


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

    ARG_NAME = 'brackets'

    def _init_arguments(self):
        self._args_parser.add_argument('**allow-redefine-ids',
                                       action='store_true')

    def __init__(self, args_sequence: Sequence[str]):
        Parser.__init__(self, args_sequence)
        self._middle_code_type = SympyLogicMiddleCode
        self._names: Dict[str, sympy.Basic] = {}

    def _parse(self, middle_code: SympyLogicMiddleCode) -> SympyLogicMiddleCode:
        middle_code.exp = self._parse_expression()
        return middle_code

    def _parse_expression(self) -> sympy.Basic:
        """
        <expression>             ::=  <conjunction>             |
                                      <disjunction>             |
                                      <negation>                |
                                      <named_expression>        |
                                      EXPRESSION_REFERENCE      |
                                      LITERAL
        """

        self._source_code.consume_leading_spaces()
        if self._source_code.current_char == self.CONJUNCTION_INIT:
            return self._parse_group(is_conjunction=True)
        elif self._source_code.current_char == self.DISJUNCTION_INIT:
            return self._parse_group(is_conjunction=False)
        elif self._source_code.current_char == self.NEGATION_OP:
            return self._parse_negation()
        elif self._source_code.current_char == self.REF_DEF_INIT:
            return self._parse_named_expression()
        elif self._source_code.current_char == self.EXP_REF_INIT:
            return self._parse_expression_reference()
        else:
            return self._parse_literal()

    def _parse_group(self, is_conjunction: bool) -> sympy.Basic:
        """
        <conjunction> ::= CONJUNCTION_INIT <expression> <expression> <expression_list> CONJUNCTION_END
        <disjunction> ::= DISJUNCTION_INIT <expression> <expression> <expression_list> DISJUNCTION_END
        """
        self._source_code.next()
        exp1 = self._parse_expression()
        exp2 = self._parse_expression()
        exp3 = self._parse_expression_list(is_conjunction)
        self._source_code.consume_leading_spaces()
        if self._source_code.current_char == (self.CONJUNCTION_END if is_conjunction else self.DISJUNCTION_END):
            self._source_code.next()
        else:
            self._parsing_critical(arg=f"'{self.CONJUNCTION_END if is_conjunction else self.DISJUNCTION_END}' "
                                       "expected")
        return sympy.And(exp1, exp2, exp3) if is_conjunction else sympy.Or(exp1, exp2, exp3)

    def _parse_expression_list(self, is_conjunction: bool) -> sympy.Basic:
        """<expression_list> ::= <expression> <expression_list> | empty_string"""
        exp = sympy.And() if is_conjunction else sympy.Or()
        self._source_code.consume_leading_spaces()
        while self._source_code.current_char != (self.CONJUNCTION_END if is_conjunction else self.DISJUNCTION_END):
            exp = (sympy.And(exp, self._parse_expression()) if is_conjunction
                   else sympy.Or(exp, self._parse_expression()))
            self._source_code.consume_leading_spaces()
        return exp

    def _parse_negation(self) -> sympy.Basic:
        """<negation> ::= NEGATION_OP <expression>"""
        self._source_code.next()
        return sympy.Not(self._parse_expression())

    def _parse_named_expression(self) -> sympy.Basic:
        """<named_expression> ::=  REFERENT_DEFINITION <expression>"""
        self._source_code.next()
        nm = self._match_id()
        if nm in self._names:
            # noinspection PyUnresolvedReferences
            if not self.allow_redefine_ids:
                self._parsing_critical(arg=f'Identifier "{nm}" has been already defined')
            else:
                self._warning(arg=f'Identifier "{nm}" has been already defined')
        sub_exp = self._parse_expression()
        self._names[nm] = sub_exp
        return sub_exp

    def _parse_expression_reference(self) -> sympy.Basic:
        self._source_code.next()
        nm = self._match_id()
        if nm not in self._names:
            self._parsing_critical(arg=f'Identifier "{nm}" has not been defined before')
        return self._names[nm]

    def _parse_literal(self) -> sympy.Symbol:
        literal = self._match_literal()
        return sympy.Symbol(literal)

    def _match_id(self) -> str:
        """
        ID = r"[a-zA-Z_][a-zA-Z0-9_]*"
        """
        id_name = ''
        alpha = string.ascii_letters + '_'
        if self._source_code.current_char not in alpha:
            self._parsing_critical(arg="Identifier expected")
        else:
            id_name += self._source_code.current_char
            self._source_code.next()
            alphanum = alpha + string.digits
            while self._source_code.current_char in alphanum:
                id_name += self._source_code.current_char
                self._source_code.next()
        return id_name

    def _match_literal(self) -> str:
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
        if self._source_code.current_char != '"':
            is_string = False
            if self._source_code.current_char in initials_finals:
                self._parsing_critical(arg='Literal expected')
        else:
            is_string = True
        literal += self._source_code.current_char
        self._source_code.next()
        invalid_chars = initials_finals + '"' + string.whitespace
        while self._source_code.current_char not in invalid_chars:
            literal += self._source_code.current_char
            self._source_code.next()
        if is_string:
            if self._source_code.current_char != '"':
                self._parsing_critical(arg='" expected')
            else:
                literal += self._source_code.current_char
                self._source_code.next()
        return literal
