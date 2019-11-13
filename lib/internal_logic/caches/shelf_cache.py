from shelve import DbfilenameShelf

from lib.internal_logic.caches.cache import InputCache
from lib.utilities.classes import Argument
from lib.utilities.enums import VerbosityLevel, XEnum


class ShelfCache(DbfilenameShelf, InputCache):
    class FileCacheMode(XEnum):
        READ = 'r'
        WRITE = 'w'
        UPDATE = 'c'
        NEW = 'n'
        DEFAULT = UPDATE

    def _init_parameters(self):
        self._filename = Argument(type=str, default='cache')
        self._mode = Argument(type=self.FileCacheMode.cast_from_name,
                              default=self.FileCacheMode.DEFAULT)
        self._in_memory_cache = Argument(type=bool, default=True)

    def __init__(self, **kwargs):
        InputCache.__init__(self, **kwargs)
        DbfilenameShelf.__init__(self, filename=self._filename,
                                 flag=self._mode.value,
                                 writeback=self._in_memory_cache)
        self._verbose_output(VerbosityLevel.DEBUG, f'Cache "{self._filename}" initialized')

    def sync(self):
        self._verbose_output(VerbosityLevel.WARNING,
                             f'Synchronizing cache "{self._filename}". '
                             '\n\tThis operation may take some time. '
                             '\n\tPlease, to avoid lost of information do not halt the program...')
        DbfilenameShelf.sync(self)
        self._verbose_output(VerbosityLevel.INFO,
                             f'Cache "{self._filename}" synchronized. ')
