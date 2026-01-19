from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, AsyncGenerator, ClassVar, TypeAlias

from fastrag.events import Event
from fastrag.helpers.experiments import Experiment
from fastrag.steps.base import IStepCommon

if TYPE_CHECKING:
    from fastrag.steps.task import Task


Tasks: TypeAlias = AsyncGenerator[tuple["Task", list[AsyncGenerator[Event, None]]], None]


@dataclass
class IStep(IStepCommon, ABC):
    description: ClassVar[str] = "UNKNOWN STEP"

    tasks: list[Task]
    experiment: Experiment | None = field(init=False, repr=False)

    def calculate_total(self) -> int:
        return len(self.tasks) if self.tasks else -1

    @abstractmethod
    async def get_tasks(self) -> Tasks:
        """Generate a dict with the tasks to perform

        Returns:
            Tasks: dict with Task instance - Async generator of callbacks
        """

        raise NotImplementedError
