from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from fastrag.cache.entry import CacheEntry
from fastrag.cache.filters import Filter
from fastrag.config.config import StepNames


@dataclass(frozen=True)
class ICache(ABC):
    base: Path
    lifespan: int

    @abstractmethod
    def is_present(self, uri: str) -> bool: ...

    @abstractmethod
    async def create(
        self,
        uri: str,
        contents: bytes,
        step: StepNames,
        metadata: dict | None = None,
    ) -> CacheEntry: ...

    @abstractmethod
    async def get_or_create(
        self,
        uri: str,
        contents: Callable[..., bytes],
        step: StepNames,
        metadata: dict | None = None,
    ) -> tuple[bool, CacheEntry]: ...

    @abstractmethod
    async def get(self, uri: str) -> CacheEntry | None: ...

    @abstractmethod
    async def get_entries(
        self, filter: Filter | None = None
    ) -> Iterable[tuple[str, CacheEntry]]: ...
