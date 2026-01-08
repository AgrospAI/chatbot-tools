from __future__ import annotations

from dataclasses import InitVar, asdict, dataclass, field
from pathlib import Path
from typing import Literal, TypeAlias, TypeVar

from fastrag.helpers.utils import parse_to_seconds


@dataclass(frozen=True)
class Strategy:
    strategy: str
    params: dict


@dataclass(frozen=True)
class Source(Strategy): ...


@dataclass(frozen=True)
class Parsing(Strategy): ...


@dataclass(frozen=True)
class Chunking(Strategy): ...


@dataclass(frozen=True)
class Embedding(Strategy): ...


@dataclass(frozen=True)
class VectorStore(Strategy): ...


@dataclass(frozen=True)
class LLM(Strategy): ...


@dataclass(frozen=True)
class Benchmarking(Strategy): ...


@dataclass(frozen=True)
class Steps:
    fetching: list[Source] | None
    parsing: list[Parsing] | None
    chunking: list[Chunking] | None
    embedding: list[Embedding] | None
    benchmarking: list[Benchmarking] | None

    asdict = asdict


StepNames: TypeAlias = Literal[
    "fetching",
    "parsing",
    "chunking",
    "embedding",
    "benchmarking",
]
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
        object.__setattr__(self, "_lifespan", parse_to_seconds(lifespan))


@dataclass(frozen=True)
class Config:
    cache: Cache
    steps: Steps
    vectorstore: VectorStore | None = None
    llm: LLM | None = None
