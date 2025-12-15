from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import TypeVar


@dataclass(frozen=True)
class Strategy:
    strategy: str
    params: dict


@dataclass(frozen=True)
class Source(Strategy): ...


@dataclass(frozen=True)
class Parsing:
    strategy: str
    use: list[str]


@dataclass(frozen=True)
class Chunking(Strategy): ...


@dataclass(frozen=True)
class Embedding(Strategy): ...


@dataclass(frozen=True)
class Benchmarking(Strategy): ...


@dataclass(frozen=True)
class Steps:
    sources: list[Source]
    parsing: list[Parsing]
    chunking: list[Chunking]
    embedding: list[Embedding]
    benchmarking: list[Benchmarking]


T = TypeVar("T", bound=Source | Parsing | Chunking | Embedding | Benchmarking)

Step = list[T]


@dataclass(frozen=True)
class Cache:
    path: Path
    _lifespan: int = field(init=False)

    lifespan: InitVar[str]

    @property
    def lifespan(self) -> int:
        return self._lifespan

    def __post_init__(self, lifespan: str) -> None:
        # To avoid circular import
        from fastrag.helpers.utils import parse_to_seconds

        object.__setattr__(self, "_lifespan", parse_to_seconds(lifespan))


@dataclass(frozen=True)
class Config:
    cache: Cache
    steps: Steps
