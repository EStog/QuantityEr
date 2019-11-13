from lib.internal_logic.caches.cache import InMemoryCache
from lib.internal_logic.caches.shelf_cache import ShelfCache
from lib.utilities.enums import XEnum


class InputCacheType(XEnum):
    SHELF = ShelfCache
    DEFAULT = SHELF


class CacheType(XEnum):
    IN_MEMORY = InMemoryCache
    SHELF = ShelfCache
    DEFAULT = IN_MEMORY


__all__ = ['CacheType', 'InputCacheType']
