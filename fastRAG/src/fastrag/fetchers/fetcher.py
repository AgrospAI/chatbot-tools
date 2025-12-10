from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import AsyncGenerator

from fastrag.config.config import Cache
from fastrag.plugins.base import PluginFactory


@dataclass(frozen=True)
class FetcherEvent:

    class Type(StrEnum):
        PROGRESS = auto()
        EXCEPTION = auto()

    type: FetcherEvent.Type
    data: any


@dataclass(frozen=True)
class Fetcher(PluginFactory, ABC):

    cache: Cache

    def __post_init__(self):
        c = self.cache

        if isinstance(c, dict):
            c = Cache(**c)

        object.__setattr__(self, "cache", c)

    @abstractmethod
    def fetch(self) -> AsyncGenerator[FetcherEvent, None]: ...
