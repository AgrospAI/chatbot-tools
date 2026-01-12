from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from typing import ClassVar, TypeAlias

from fastrag.helpers.utils import parse_to_seconds


@dataclass(frozen=True)
class Strategy:
    strategy: str
    params: dict


Steps: TypeAlias = dict[str, list[Strategy]]


@dataclass(frozen=True)
class Sources:
    steps: Steps
    strategy: str = "async"


@dataclass(frozen=True)
class Experiments:
    steps: Steps
    strategy: str = "async"


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
class Cache:
    strategy: str = field(default="local")
    _lifespan: int = field(init=False)

    lifespan: InitVar[str | None]
    default_lifespan: ClassVar[str] = "1d"

    @property
    def lifespan(self) -> int:
        return self._lifespan

    def __post_init__(self, lifespan: str) -> None:
        object.__setattr__(
            self, "_lifespan", parse_to_seconds(lifespan or Cache.default_lifespan)
        )


@dataclass(frozen=True)
class Resources:
    sources: Sources
    cache: Cache = field(default_factory=Cache)
    store: VectorStore | None = field(default=None)
    llm: Strategy | None = field(default=None)


@dataclass(frozen=True)
class Config:
    resources: Resources
    experiments: Experiments
    benchmarking: list[Strategy]
