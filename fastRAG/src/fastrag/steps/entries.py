from abc import ABC
from asyncio import Lock
from typing import List

from fastrag.cache.entry import CacheEntry
from fastrag.helpers.filters import Filter


class Entries(ABC):

    _lock: Lock = Lock()
    entries: List[CacheEntry] = None
    filter: Filter[CacheEntry] = None

    def __init__(self) -> None:
        self.uri: str | None
        self.entry: CacheEntry | None

        object.__setattr__(self, "uri", None)
        object.__setattr__(self, "entry", None)

    async def init_entries(self) -> None:
        assert (
            getattr(self, "cache", None) is not None
        ), f"{self.__class__.__name__} must have 'cache'"

        cls = type(self)

        async with cls._lock:
            if cls.entries is None:
                cls.entries = await self.cache.get_entries(self.filter)
            if not cls.entries:
                raise RuntimeError(f"No more entries available for {cls.__name__}")

            uri, entry = cls.entries.pop(0)

            object.__setattr__(self, "uri", uri)
            object.__setattr__(self, "entry", entry)
