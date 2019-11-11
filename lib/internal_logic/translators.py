import re
from abc import abstractmethod
from typing import Set

from lib.utilities.classes import WithDefaults
from lib.utilities.flip_dict import Flipdict
from lib.utilities.functions import normalize_name


class Translator(WithDefaults):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def _get_translated_set_query(query: Set[str], associations: Flipdict) -> Set[str]:
        translated_query = set()
        for q in query:
            m = re.match(r'~(.+)', q)
            if m:
                translated_query |= {f'~{associations[m.group(1)]}'}
            else:
                translated_query |= {associations[q]}
        return translated_query

    @abstractmethod
    def get_particular_query(self, query: Set[str], associations: Flipdict) -> str:
        pass


class SpacesTranslator(Translator):
    """
    Translator that convert a set of keywords in an whitespace-separated string
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_particular_query(self, query: Set[str], associations: Flipdict) -> str:
        """
        This method expects an expression in the form (<v1> & <v2> & ... & <vn>) where
        <vi> for 1 <= i <= n is the name of the i-th variable each of them may or not be
        affected by a negation(~).
        """
        particular_query = ''
        for q in sorted(self._get_translated_set_query(query, associations)):
            m = re.match(r'~(.+)', q)
            if m:
                particular_query += f' NOT {m.group(1)}'
            else:
                particular_query += f' {q}'
        return particular_query[1:].lower()


SpacesTranslator.__name__ = normalize_name(SpacesTranslator.__name__)

__all__ = ['Translator', 'SpacesTranslator']
