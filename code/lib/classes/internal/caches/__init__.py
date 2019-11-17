from lib.classes.internal.caches.in_memory_cache import InMemoryCache
from lib.classes.internal.caches.shelf_cache import ShelfCache

INPUT_CACHE_TYPE = {
    ShelfCache.ARG_NAME: ShelfCache
}

CACHE_TYPE = {
    InMemoryCache.ARG_NAME: InMemoryCache,
    ShelfCache.ARG_NAME: ShelfCache
}

DEFAULT_CACHE_TYPE = InMemoryCache.ARG_NAME
