from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import InitVar, dataclass, field
from typing import AsyncGenerator, ClassVar, TypeAlias

from fastrag.cache.cache import ICache
from fastrag.cache.entry import CacheEntry
from fastrag.cache.filters import Filter
from fastrag.events import Event
from fastrag.helpers.experiments import Experiment
from fastrag.helpers.resources import RuntimeResources
from fastrag.llms.llm import ILLM
from fastrag.plugins import PluginBase
from fastrag.stores.store import IVectorStore

Run: TypeAlias = AsyncGenerator[Event, None]


class ITask(PluginBase, ABC):
    @abstractmethod
    async def run(self, uri: str | None = None, entry: CacheEntry | None = None) -> Run:
        """Base callback to run all tasks with

        Args:
            uri (str | None, optional): Entry URI. Defaults to None.
            entry (CacheEntry | None, optional): Entry. Defaults to None.

        Yields:
            Event: task event
        """

        raise NotImplementedError

    @abstractmethod
    def completed_callback(self) -> Event:
        """Called when the task has been completed. Mainly for logging purposes.

        Returns:
            Event: Completed event
        """

        raise NotImplementedError


@dataclass(slots=True)
class Task[T](ITask, ABC):
    filter: ClassVar[Filter | None] = None

    resources: RuntimeResources = field(repr=False)

    experiment: Experiment | None = field(init=False, repr=False)
    results: T | None = field(default=None, init=False, repr=False)

    @property
    def cache(self) -> ICache:
        return self.resources.cache

    @property
    def store(self) -> IVectorStore:
        return self.resources.store

    @property
    def llm(self) -> ILLM:
        return self.resources.llm
