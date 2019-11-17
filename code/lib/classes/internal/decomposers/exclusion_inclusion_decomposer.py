from itertools import combinations
from typing import Iterable

import sympy
from sympy import simplify_logic, to_dnf

from lib.classes.internal.decomposers.decomposer import Decomposer
from lib.classes.internal.middle_codes.middle_code import MiddleCode
from lib.classes.internal.middle_codes.sympy_logic_middle_code import SympyLogicMiddleCode


class ExclusionInclusionDecomposer(Decomposer):

    def __init__(self, deep_simplify=False):
        Decomposer.__init__(self)
        self._deep_simplify = deep_simplify
        self._terms = None

    def set_middle_code(self, middle_code: MiddleCode):
        Decomposer.set_middle_code(self, middle_code)
        self._convert_to_dnf()
        if (isinstance(self._middle_code.exp, sympy.Symbol) or
                isinstance(self._middle_code.exp, sympy.And)):
            self._terms = (self._middle_code.exp,)
        else:
            self._terms = self._middle_code.exp.args
        self._debug(f'Disjunctive normal form terms number', arg=len(self._terms))

    def longest_subexpression(self) -> SympyLogicMiddleCode:
        return SympyLogicMiddleCode(exp=simplify_logic(self._middle_code.exp.replace(sympy.Or, sympy.And)))

    def _convert_to_dnf(self):
        self._debug(f'Converting to DNF ...', header=self._middle_code.full_name)
        exp = simplify_logic(self._middle_code.exp, form='dnf', force=self._deep_simplify)
        self._middle_code.exp = to_dnf(exp)
        self._debug(f'Converted to DNF', header=self._middle_code.full_name)

    def get_subqueries(self) -> Iterable[MiddleCode]:
        """This method implements an inclusion-exclusion principle"""
        sum_factor = 1
        i = 0
        for p in range(1, len(self._terms) + 1):
            for comb in combinations(self._terms, p):
                i += 1
                yield SympyLogicMiddleCode(
                    namespace=self._middle_code.full_name,
                    name=str(i),
                    exp=sympy.And(*comb)
                ), sum_factor
            sum_factor *= -1

    def get_sub_queries_amount(self) -> int:
        return 2 ** len(self._terms) - 1
