from abc import ABC, abstractmethod
from typing import Sequence

from lib.classes import WithLoggingAndExternalArguments


class Cache(dict, WithLoggingAndExternalArguments, ABC):
    def __init__(self, args_sequence: Sequence):
        WithLoggingAndExternalArguments.__init__(self, args_sequence)
        dict.__init__(self)

    def reset(self):
        self._debug(f'Resetting...')
        self._reset()
        self._debug(f'Reset')

    @abstractmethod
    def _reset(self):
        pass
