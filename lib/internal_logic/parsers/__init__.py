from lib.internal_logic.parsers.brackets_syntax_parser import BracketsSyntaxParser
from lib.utilities.enums import XEnum


class SyntaxType(XEnum):
    BRACKETS = BracketsSyntaxParser
    DEFAULT = BRACKETS


__all__ = ['SyntaxType']
