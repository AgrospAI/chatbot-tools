from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generator, TypeAlias

from fastrag.events import Event
from fastrag.plugins.base import IPluginFactory

ParsingEvent: TypeAlias = Event


@dataclass(frozen=True)
class IParser(IPluginFactory, ABC):

    @abstractmethod
    def parse(self) -> Generator[ParsingEvent, None, None]: ...
