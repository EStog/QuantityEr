from abc import abstractmethod
from typing import Iterable

from lib.classes.internal.middle_codes.middle_code import MiddleCode
from lib.utilities.logging.with_logging import WithLogging


class Decomposer(WithLogging):

    def __init__(self):
        WithLogging.__init__(self)
        self._middle_code = None

    @abstractmethod
    def get_subqueries(self) -> Iterable[MiddleCode]:
        pass

    @abstractmethod
    def get_sub_queries_amount(self) -> int:
        pass

    @abstractmethod
    def longest_subexpression(self) -> MiddleCode:
        pass

    def set_middle_code(self, middle_code: MiddleCode):
        self._middle_code = middle_code
