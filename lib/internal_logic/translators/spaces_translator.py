import re
from typing import Set, Mapping

from lib.internal_logic.translators.translator import Translator
from lib.utilities.functions import normalize_name


class SpacesTranslator(Translator):
    """
    Translator that convert a set of keywords in an whitespace-separated string
    """

    def _init_parameters(self):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_particular_query(self, query: Set[str],
                             symbols_table: Mapping[str, str]) -> str:
        """
        This method expects an expression in the form (<v1> & <v2> & ... & <vn>) where
        <vi> for 1 <= i <= n is the name of the i-th variable each of them may or not be
        affected by a negation(~).
        """
        particular_query = ''
        for q in sorted(self._get_translated_set_query(query, symbols_table)):
            m = re.match(r'~(.+)', q)
            if m:
                particular_query += f' NOT {m.group(1)}'
            else:
                particular_query += f' {q}'
        return particular_query[1:].lower()


SpacesTranslator.__name__ = normalize_name(SpacesTranslator.__name__)

__all__ = ['SpacesTranslator']
