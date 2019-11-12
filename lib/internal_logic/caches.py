from shelve import DbfilenameShelf

from lib.utilities.classes import WithDefaults, Firm
from lib.utilities.enums import XEnum, VerbosityLevel


class Cache(dict, WithDefaults):

    def __init__(self, **kwargs):
        dict.__init__(self)
        WithDefaults.__init__(self, **kwargs)

    def close(self):
        pass

    def sync(self):
        pass


class InMemoryCache(Cache):
    pass


class InputCache(Cache):
    pass


class FileCacheMode(XEnum):
    READ = 'r'
    WRITE = 'w'
    UPDATE = 'c'
    NEW = 'n'
    DEFAULT = UPDATE


class ShelfCache(DbfilenameShelf, InputCache):
    class _KW(XEnum):
        FILENAME = Firm(ttype=str, default='cache')
        MODE = Firm(ttype=FileCacheMode.cast_from_name, default=FileCacheMode.DEFAULT)
        IN_MEMORY_CACHE = Firm(ttype=bool, default=True)

    def __init__(self, **kwargs):
        Cache.__init__(self, **kwargs)
        DbfilenameShelf.__init__(self, filename=self._get(self._KW.FILENAME),
                                 flag=self._get(self._KW.MODE).value,
                                 writeback=self._get(self._KW.IN_MEMORY_CACHE))
        self._verbose_output(VerbosityLevel.DEBUG, f'Cache "{self._get(self._KW.FILENAME)}" initialized')

    def sync(self):
        self._verbose_output(VerbosityLevel.WARNING,
                             f'Synchronizing cache "{self._get(self._KW.FILENAME)}". '
                             '\n\tThis operation may take some time. '
                             '\n\tPlease, to avoid lost of information do not halt the program...')
        DbfilenameShelf.sync(self)
        self._verbose_output(VerbosityLevel.INFO,
                             f'Cache "{self._get(self._KW.FILENAME)}" synchronized. ')


class InputCacheType(XEnum):
    SHELF = ShelfCache
    DEFAULT = SHELF


class CacheType(XEnum):
    IN_MEMORY = InMemoryCache
    SHELF = ShelfCache
    DEFAULT = IN_MEMORY


__all__ = ['Cache', 'CacheType','InputCacheType']
