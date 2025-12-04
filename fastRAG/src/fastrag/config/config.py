from dataclasses import dataclass
from pathlib import Path


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


@dataclass(frozen=True)
class Steps:
    sources: Source
    parsing: Parsing
    chunking: Chunking
    embedding: Embedding
    benchmarking: Benchmarking


@dataclass(frozen=True)
class Config:
    cache: Path
    steps: Steps
