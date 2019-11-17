import sympy

from lib.classes.internal.middle_codes.middle_code import MiddleCode


class SympyLogicMiddleCode(MiddleCode):
    def __init__(self, namespace: str = '', name: str = '', exp: sympy.Basic = None):
        MiddleCode.__init__(self, namespace, name)
        if exp:
            self.exp = exp
        else:
            self.exp = sympy.Basic()

    def __repr__(self):
        return f'{self.__class__.__name__}({self.exp!s})'
