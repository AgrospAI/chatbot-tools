from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncGenerator

from fastrag.cache.cache import ICache
from fastrag.cache.entry import CacheEntry
from fastrag.events import Event


@dataclass(frozen=True)
class Task(ABC):
    cache: ICache = field(compare=False, hash=False)

    @abstractmethod
    async def callback(
        self,
        uri: str | None = None,
        entry: CacheEntry | None = None,
    ) -> AsyncGenerator[Event, None]:
        """Base callback to run all tasks with

        Args:
            uri (str | None, optional): Entry URI. Defaults to None.
            entry (CacheEntry | None, optional): Entry. Defaults to None.

        Yields:
            Event: task event
        """

        raise NotImplementedError

    def completed_callback(self) -> Event:
        """Called when the task has been completed. Mainly for logging purposes.

        Returns:
            Event: Completed event
        """

        raise NotImplementedError
