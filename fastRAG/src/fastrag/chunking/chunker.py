from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeAlias

from fastrag.events import Event
from fastrag.plugins.base import IPluginFactory

ChunkingEvent: TypeAlias = Event


class Chunker(IPluginFactory, ABC):

    @classmethod
    @abstractmethod
    def chunk(cls, path: Path) -> None: ...
