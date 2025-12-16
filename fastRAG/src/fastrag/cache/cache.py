from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Literal

from fastrag.helpers.utils import PosixTimestamp, timestamp
from fastrag.plugins.base import PluginFactory

CacheSection = Literal[
    "sourcing",
    "parsing",
    "chunking",
    "embedding",
    "benchmarking",
]


@dataclass(frozen=True)
class CacheEntry:

    content_hash: str
    section: CacheSection
    path: Path
    timestamp: PosixTimestamp = field(default_factory=timestamp)
    metadata: dict | None = field(default=None)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["path"] = str(self.path.resolve().as_uri())
        return d

    @staticmethod
    def from_dict(d: dict) -> CacheEntry:
        d = dict(d)
        d["path"] = Path(d["path"])
        return CacheEntry(**d)


@dataclass(frozen=True)
class ICache(PluginFactory, ABC):

    base: Path
    lifespan: int

    @abstractmethod
    def is_present(self, uri: str) -> bool: ...

    @abstractmethod
    async def create(
        self,
        uri: str,
        contents: bytes,
        section: CacheSection,
        metadata: dict | None = None,
    ) -> CacheEntry: ...

    @abstractmethod
    async def get_or_create(
        self,
        uri: str,
        contents: Callable[..., bytes],
        section: CacheSection,
        metadata: dict | None = None,
    ) -> tuple[bool, CacheEntry]: ...

    @abstractmethod
    async def get(self, uri: str) -> CacheEntry | None: ...

    @abstractmethod
    async def get_entries(self, section: CacheSection) -> Iterable[CacheEntry]: ...
