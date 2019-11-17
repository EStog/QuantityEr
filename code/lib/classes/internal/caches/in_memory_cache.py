from typing import Sequence

from lib.classes.internal.caches.cache import Cache


class InMemoryCache(Cache):
    ARG_NAME = 'in-memory'

    def __init__(self, args_sequence: Sequence):
        Cache.__init__(self, args_sequence)
        dict.__init__(self)

    def _init_arguments(self):
        pass

    def _reset(self):
        dict.__init__(self)
