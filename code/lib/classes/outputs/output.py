from abc import abstractmethod

from lib.classes.internal.middle_codes.middle_code import MiddleCode
from lib.utilities.logging.with_logging import WithLogging


class Output(WithLogging):

    def __init__(self):
        WithLogging.__init__(self)

    @abstractmethod
    def output(self, middle_code: MiddleCode, simulate: bool, results):
        pass
