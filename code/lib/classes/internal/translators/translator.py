from abc import abstractmethod

from lib.classes.internal.middle_codes.middle_code import MiddleCode
from lib.utilities.logging.with_logging import WithLogging


class Translator(WithLogging):
    def __init__(self):
        WithLogging.__init__(self)

    @abstractmethod
    def get_particular_query(self, middle_code: MiddleCode) -> str:
        pass
