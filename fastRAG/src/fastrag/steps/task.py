from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncGenerator

from fastrag.cache.cache import ICache
from fastrag.events import Event


@dataclass(frozen=True)
class Task(ABC):
    cache: ICache = field(compare=False, hash=False)

    @abstractmethod
    async def callback(self) -> AsyncGenerator[Event, None]:
        """Base callback to run with all tasks

        Yields:
            Event:
        """

        raise NotImplementedError

    def completed_callback(self) -> Event:
        """Called when the task has been completed. Mainly for logging purposes.

        Returns:
            Event: Completed event
        """

        raise NotImplementedError
