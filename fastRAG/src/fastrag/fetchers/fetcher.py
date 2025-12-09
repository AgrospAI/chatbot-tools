from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from fastrag.config.config import Cache
from fastrag.plugins.base import PluginFactory


@dataclass(frozen=True)
class Fetcher(PluginFactory, ABC):

    cache: Cache

    def __post_init__(self):
        c = self.cache

        if isinstance(c, dict):
            c = Cache(**c)

        object.__setattr__(self, "cache", c)

    @abstractmethod
    def fetch(self) -> Iterable[Path]: ...
