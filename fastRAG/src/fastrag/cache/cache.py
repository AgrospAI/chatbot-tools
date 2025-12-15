from __future__ import annotations

from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

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
    timestamp: int = field(default_factory=lambda: datetime.now().timestamp())
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
class CacheEntryInput: ...


@dataclass(frozen=True)
class ICache(PluginFactory, ABC):

    base: Path
    lifespan: int

    def is_outdated(self, timestamp: int) -> bool:
        return timestamp + self.lifespan < datetime.now().timestamp()

    @abstractmethod
    def is_present(self, uri: str) -> bool: ...

    @abstractmethod
    def hash(self, content: str) -> str: ...

    @abstractmethod
    async def store(
        self,
        uri: str,
        contents: bytes,
        section: CacheSection,
        metadata: dict | None = None,
    ) -> CacheEntry: ...

    @abstractmethod
    async def get(self, uri: str) -> CacheEntry | None: ...
