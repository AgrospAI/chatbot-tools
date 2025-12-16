from abc import ABC, abstractmethod
from typing import AsyncGenerator, TypeAlias

from fastrag.events import Event
from fastrag.plugins.base import IPluginFactory

FetchingEvent: TypeAlias = Event


class IFetcher(IPluginFactory, ABC):

    @abstractmethod
    async def fetch(self) -> AsyncGenerator[FetchingEvent, None]: ...
