from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncGenerator, Iterable, List

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
        """Calculates the number of tasks to perform by this step

        Returns:
            int: number of tasks to perform
        """
        return len(self.step) if self.step else 0

    @property
    def is_present(self) -> bool:
        """If the step is present"""
        return self.step is not None

    @abstractmethod
    def get_tasks(self) -> List[AsyncGenerator[Event, None]]:
        """Generate a list with the tasks to perform

        Returns:
            List[AsyncGenerator[Event, None]]: list with the different tasks
        """

        raise NotImplementedError
