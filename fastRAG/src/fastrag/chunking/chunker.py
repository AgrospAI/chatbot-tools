from abc import ABC, abstractmethod
from pathlib import Path

from fastrag.plugins.base import PluginFactory


class Chunker(PluginFactory, ABC):

    @classmethod
    @abstractmethod
    def chunk(cls, path: Path) -> None: ...
