import re
from abc import abstractmethod
from typing import FrozenSet

from lib.utilities.classes import WithDefaults
from lib.utilities.flip_dict import Flipdict
from lib.utilities.functions import normalize_name


class Translator(WithDefaults):
    def __init__(self, associations: Flipdict):
        super().__init__()
        self._associations = associations

    @abstractmethod
    def get_translated_query(self, query: FrozenSet[str]) -> str:
        pass


class SpacesTranslator(Translator):
    """
    Translator that convert a set of keywords in an whitespace-separated string
    """

    def __init__(self, associations: Flipdict):
        super().__init__(associations)

    def get_translated_query(self, query: FrozenSet[str]) -> str:
        """
        This method expects an expression in the form (<v1> & <v2> & ... & <vn>) where
        <vi> for 1 <= i <= n is the name of the i-th variable each of them may or not be
        affected by a negation(~).
        """
        particular_query = ''
        for q in query:
            if re.match(r'~.+', q):
                particular_query += f' NOT {self._associations[q]}'
            else:
                particular_query += f' {self._associations[q]}'
        return particular_query[1:]


SpacesTranslator.__name__ = normalize_name(SpacesTranslator.__name__)

__all__ = ['Translator', 'SpacesTranslator']
