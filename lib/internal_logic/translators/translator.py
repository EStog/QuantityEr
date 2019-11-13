import re
from abc import abstractmethod
from typing import Set, Mapping

from lib.utilities.classes import WithArguments


class Translator(WithArguments):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def _get_translated_set_query(query: Set[str],
                                  symbols_table: Mapping[str, str]) -> Set[str]:
        translated_query = set()
        for q in query:
            m = re.match(r'~(.+)', q)
            if m:
                translated_query |= {f'~{symbols_table[m.group(1)]}'}
            else:
                translated_query |= {symbols_table[q]}
        return translated_query

    @abstractmethod
    def get_particular_query(self, query: Set[str],
                             symbols_table: Mapping[str, str]) -> str:
        pass


__all__ = ['Translator']
