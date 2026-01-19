from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, AsyncGenerator, ClassVar, TypeAlias, override

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

    @override
    def calculate_total(self) -> int:
        return len(self.tasks) if self.tasks else -1
