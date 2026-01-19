from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, ClassVar, TypeAlias

from fastrag.cache.cache import ICache
from fastrag.cache.entry import CacheEntry
from fastrag.events import Event
from fastrag.helpers.experiments import Experiment
from fastrag.helpers.filters import Filter
from fastrag.llms.llm import ILLM
from fastrag.plugins import PluginBase
from fastrag.steps.resources import RuntimeResources
from fastrag.stores.store import IVectorStore

Run: TypeAlias = AsyncGenerator[Event, None]


@dataclass(frozen=True)
class Task(PluginBase, ABC):
    _results: Any = field(init=False, repr=False, compare=False, hash=False)
    resources: RuntimeResources = field(compare=False, hash=False, repr=False)
    experiment: Experiment | None = field(init=False, compare=False, hash=False, repr=False)

    filter: ClassVar[Filter | None] = None

    def set_experiment(self, experiment: Experiment):
        object.__setattr__(self, "experiment", experiment)

    def set_results(self, value: Any) -> None:
        object.__setattr__(self, "_results", value)

    @property
    def cache(self) -> ICache:
        return self.resources.cache

    @property
    def store(self) -> IVectorStore:
        return self.resources.store

    @property
    def llm(self) -> ILLM:
        return self.resources.llm

    @property
    def results(self) -> Any:
        return getattr(self, "_results", None)

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
