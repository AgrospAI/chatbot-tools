from abc import ABC, abstractmethod
from typing import AsyncGenerator, TypeAlias

from fastrag.events import Event
from fastrag.plugins.base import IPluginFactory

EmbeddingEvent: TypeAlias = Event


class IEmbedder(IPluginFactory, ABC):

    @abstractmethod
    async def embed(self) -> AsyncGenerator[EmbeddingEvent, None]: ...
