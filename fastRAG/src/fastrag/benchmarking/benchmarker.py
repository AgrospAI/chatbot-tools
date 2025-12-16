from abc import ABC, abstractmethod
from typing import AsyncGenerator, TypeAlias

from fastrag.events import Event
from fastrag.plugins.base import IPluginFactory

BenchmarkingEvent: TypeAlias = Event


class IBenchmarker(IPluginFactory, ABC):

    @abstractmethod
    async def benchmark(self) -> AsyncGenerator[BenchmarkingEvent, None]: ...
