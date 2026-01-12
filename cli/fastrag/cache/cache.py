from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Iterable

from fastrag.cache.entry import CacheEntry
from fastrag.cache.filters import Filter
from fastrag.plugins import PluginBase


@dataclass(frozen=True)
class ICache(PluginBase, ABC):
    lifespan: int

    @abstractmethod
    def is_present(self, uri: str) -> bool:
        """Checks if the entry is present and has valid lifetime

        Args:
            uri (str): resource URI

        Returns:
            bool: if present and valid
        """

        raise NotImplementedError

    @abstractmethod
    async def create(
        self,
        uri: str,
        contents: bytes,
        metadata: dict | None = None,
    ) -> CacheEntry:
        """Creates a new entry

        Args:
            uri (str): resource URI
            contents (bytes): contents to store
            metadata (dict | None, optional): additional metadata. Defaults to None.

        Returns:
            CacheEntry: created entry
        """

        raise NotImplementedError

    @abstractmethod
    async def get_or_create(
        self,
        uri: str,
        contents: Callable[..., bytes],
        metadata: dict | None = None,
    ) -> tuple[bool, CacheEntry]:
        """Returns the cache entry from URI if it exists, otherwise creates it.

        Args:
            uri (str): URI to check (or create entry with)
            contents (Callable[..., bytes]): callable that will read the contents to store.
            metadata (dict | None, optional): Additional metadata to store. Defaults to None.

        Returns:
            tuple[bool, CacheEntry]: if it already existed, the entry
        """

        raise NotImplementedError

    @abstractmethod
    async def get(self, uri: str) -> CacheEntry | None:
        """Gets a cache entry from the given URI

        Args:
            uri (str): URI of the entry

        Returns:
            CacheEntry | None: Cache entry
        """

        raise NotImplementedError

    @abstractmethod
    async def get_entries(
        self, filter: Filter | None = None
    ) -> Iterable[tuple[str, CacheEntry]]:
        """Get the entries that pass the given filter

        Args:
            filter (Filter | None, optional): Filter that the entries must pass.
            Defaults to None.

        Returns:
            Iterable[tuple[str, CacheEntry]]: Entries
        """

        raise NotImplementedError

    @abstractmethod
    def clean(self) -> int:
        """Cleans the cache

        Returns:
            int: cleaned size
        """

        raise NotImplementedError
