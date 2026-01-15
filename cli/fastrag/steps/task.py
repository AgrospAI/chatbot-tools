from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, AsyncGenerator, TypeAlias

from fastrag.cache.cache import ICache
from fastrag.cache.entry import CacheEntry
from fastrag.events import Event
from fastrag.llms.llm import ILLM
from fastrag.plugins import PluginBase
from fastrag.steps.step import RuntimeResources
from fastrag.stores.store import IVectorStore

if TYPE_CHECKING:
    from fastrag.helpers.experiments import Experiment

Run: TypeAlias = AsyncGenerator[Event, None]


@dataclass(frozen=True)
class Task(PluginBase, ABC):
    _results: Any = field(init=False, repr=False, compare=False, hash=False)
    experiment: Experiment = field(compare=False, hash=False, repr=False)
    resources: RuntimeResources = field(compare=False, hash=False, repr=False)

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

    def _set_results(self, value: Any) -> None:
        object.__setattr__(self, "_results", value)

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
