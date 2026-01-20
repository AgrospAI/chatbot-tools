from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import ClassVar, override

from fastrag.helpers.experiments import Experiment
from fastrag.steps.base import IStepCommon
from fastrag.tasks.base import ITask


@dataclass
class IStep(IStepCommon, ABC):
    description: ClassVar[str] = "UNKNOWN STEP"

    _experiment: Experiment | None = field(init=False, repr=False)
    tasks: list[ITask]

    @property
    def experiment(self) -> Experiment | None:
        return self._experiment

    @experiment.setter
    def experiment(self, value: Experiment) -> None:
        self._experiment = value
        for task in self.tasks:
            task.experiment = value

    @override
    def calculate_total(self) -> int:
        return len(self.tasks) if self.tasks else -1
