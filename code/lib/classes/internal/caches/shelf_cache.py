from shelve import DbfilenameShelf
from typing import Sequence

from lib.classes.internal.caches.cache import Cache
from lib.utilities.logging import ExitCode


class ShelfCache(DbfilenameShelf, Cache):
    FILE_CACHE_MODE = {
        'read': 'r',
        'write': 'w',
        'update': 'c',
        'new': 'n'
    }
    DEFAULT_MODE = 'update'

    ARG_NAME = 'shelf'

    def _init_arguments(self):
        self._args_parser.add_argument('filename', metavar='FILENAME',
                                       default='cache', nargs='?')
        self._args_parser.add_argument('**mode',
                                       default=self.DEFAULT_MODE,
                                       choices=self.FILE_CACHE_MODE.keys())
        self._args_parser.add_argument('**in-memory-cache',
                                       action='store_true')

    def __init__(self, args_sequence: Sequence, as_input_cache=False):
        Cache.__init__(self, args_sequence)
        try:
            if as_input_cache:
                # noinspection PyUnresolvedReferences
                DbfilenameShelf.__init__(self, filename=self.filename,
                                         flag='r')
            else:
                # noinspection PyUnresolvedReferences
                DbfilenameShelf.__init__(self, filename=self.filename,
                                         flag=self.FILE_CACHE_MODE[self.mode],
                                         writeback=self.in_memory_cache)
        except IOError as e:
            self._critical('Error while opening cache', ExitCode.FILE_ERROR, e)
        # noinspection PyUnresolvedReferences
        self._debug(f' Initialized', header=f'Cache "{self.filename}"')

    def _reset(self):
        # noinspection PyUnresolvedReferences
        DbfilenameShelf.__init__(self, filename=self.filename,
                                 flag='n',
                                 writeback=self.in_memory_cache)

    def sync(self):
        # noinspection PyUnresolvedReferences
        self._debug(f'Synchronizing...',
                    header=f'Cache "{self.filename}"')
        DbfilenameShelf.sync(self)
        # noinspection PyUnresolvedReferences
        self._debug('Synchronized', header=f'Cache "{self.filename}"')
