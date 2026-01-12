from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from typing import ClassVar, TypeAlias

from fastrag.helpers.utils import parse_to_seconds


@dataclass(frozen=True)
class Strategy:
    strategy: str
    params: dict | None


Step: TypeAlias = list[Strategy]
Steps: TypeAlias = dict[str, list[Strategy]]


@dataclass(frozen=True)
class MultiStrategy:
    steps: Steps
    strategy: str = "async"


@dataclass(frozen=True)
class Cache:
    lifespan_str: InitVar[str] = "1d"
    strategy: str = field(default="local")
    _lifespan: int = field(init=False)

    @property
    def lifespan(self) -> int:
        return self._lifespan

    def __post_init__(self, lifespan_str: str) -> None:
        object.__setattr__(
            self,
            "_lifespan",
            parse_to_seconds(lifespan_str),
        )


@dataclass(frozen=True)
class Resources:
    sources: MultiStrategy
    cache: Cache = field(default_factory=Cache)
    store: Strategy | None = field(default=None)
    llm: Strategy | None = field(default=None)


@dataclass(frozen=True)
class Config:
    resources: Resources
    experiments: MultiStrategy
    benchmarking: list[Strategy]
