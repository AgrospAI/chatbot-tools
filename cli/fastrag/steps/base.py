from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import InitVar, dataclass, field
from typing import AsyncGenerator, TypeAlias

from rich.progress import Progress

from fastrag.cache.cache import ICache
from fastrag.events import Event
from fastrag.helpers.resources import RuntimeResources
from fastrag.llms.llm import ILLM
from fastrag.plugins import PluginBase, inject
from fastrag.steps.logs import Loggable
from fastrag.stores.store import IVectorStore
from fastrag.tasks.base import ITask

Tasks: TypeAlias = AsyncGenerator[tuple[ITask, list[AsyncGenerator[Event, None]]], None]


@dataclass
class IStepCommon(PluginBase, ABC):
    progress: InitVar[Progress]

    task_id: int
    resources: RuntimeResources = field(repr=False)
    logger: Loggable = field(init=False, repr=False)

    def __post_init__(self, progress: Progress) -> None:
        self.logger = inject(Loggable, "rich", progress=progress)

    @property
    def cache(self) -> ICache:
        return self.resources.cache

    @property
    def store(self) -> IVectorStore:
        return self.resources.store

    @property
    def llm(self) -> ILLM:
        return self.resources.llm

    @abstractmethod
    def calculate_total(self) -> int:
        """Calculates the number of tasks to perform by this step

        Returns:
            int: number of tasks to perform
        """

        raise NotImplementedError

    @abstractmethod
    async def get_tasks(self) -> Tasks:
        """Generate a dict with the tasks to perform

        Returns:
            Tasks: dict with Task instance - Async generator of callbacks
        """

        raise NotImplementedError
