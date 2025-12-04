from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class Strategy:
    strategy: str
    params: dict[str, str]


@dataclass(frozen=True)
class Source(Strategy): ...


@dataclass(frozen=True)
class Parsing(Strategy): ...


@dataclass(frozen=True)
class Chunking(Strategy): ...


@dataclass(frozen=True)
class Embedding(Strategy): ...


@dataclass(frozen=True)
class Benchmarking(Strategy): ...


Step = List[Source] | Parsing | Chunking | Embedding | Benchmarking


@dataclass(frozen=True)
class Config:
    cache: Path
    steps: List[Step]
