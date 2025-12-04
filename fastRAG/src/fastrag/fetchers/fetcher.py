from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from fastrag.plugins.base import PluginFactory


class Fetcher(PluginFactory, ABC):

    @classmethod
    @abstractmethod
    def fetch(cls, value: str) -> Iterable[Path]: ...
