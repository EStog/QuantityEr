from lib.utilities.classes import WithArguments


class Cache(dict, WithArguments):
    def __init__(self, **kwargs):
        dict.__init__(self)
        WithArguments.__init__(self, **kwargs)


class InMemoryCache(Cache):
    pass


class InputCache(Cache):
    pass


__all__ = ['Cache', 'InputCache', 'InMemoryCache']
