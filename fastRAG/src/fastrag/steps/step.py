from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncGenerator, Iterable

from rich.progress import Progress

from fastrag.config.config import Step
from fastrag.events import Event
from fastrag.steps.logs import Loggable


@dataclass(frozen=True)
class IStep(Loggable, ABC):

    step: Step
    progress: Progress
    task_id: int

    def calculate_total(self) -> int:
        return len(self.step) if self.step else 0

    @property
    def is_present(self) -> bool:
        return self.step is not None

    @abstractmethod
    def get_tasks(self) -> Iterable[AsyncGenerator[Event, None]]: ...
