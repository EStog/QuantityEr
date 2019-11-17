import sympy

from lib.classes.internal.middle_codes.sympy_logic_middle_code import SympyLogicMiddleCode
from lib.classes.internal.translators.translator import Translator


class SpacesTranslator(Translator):
    """
    Translator that convert a set of keywords in an whitespace-separated string
    """

    def __init__(self):
        Translator.__init__(self)

    def get_particular_query(self, conjunction_middle_code: SympyLogicMiddleCode) -> str:
        particular_query = ''

        if isinstance(conjunction_middle_code.exp, sympy.Symbol):
            return str(conjunction_middle_code.exp)
        else:
            for symbol in sorted(conjunction_middle_code.exp.args, key=lambda a: str(a)):
                if isinstance(symbol, sympy.Not):
                    particular_query += f'NOT {symbol[1:]} '
                else:
                    particular_query += f'{symbol} '
            return particular_query[:-1]
