from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Dict

from rich.progress import Progress

from fastrag.cache.cache import ICache
from fastrag.config.config import Step
from fastrag.constants import get_constants
from fastrag.events import Event
from fastrag.steps.logs import Loggable
from fastrag.steps.task import Task


@dataclass
class IStep(Loggable, ABC):

    step: Step
    progress: Progress
    task_id: int
    description: ClassVar[str] = ""
    _tasks: ClassVar[Dict[str, Task]] = None

    def calculate_total(self) -> int:
        """Calculates the number of tasks to perform by this step

        Returns:
            int: number of tasks to perform
        """
        return len(self.step) if self.step else 0

    @property
    def is_present(self) -> bool:
        """If the step has been loaded / is present in the configuration file"""
        return self.step is not None

    async def tasks(self) -> Dict[str, Task]:
        if self._tasks is None:
            cache = get_constants().cache
            self._tasks = await self.get_tasks(cache)
        return self._tasks

    @abstractmethod
    async def get_tasks(self, cache: ICache) -> Dict[Task, AsyncGenerator[Event, None]]:
        """Generate a dict with the tasks to perform

        Returns:
            Dict[Task, AsyncGenerator[Event, None]]: Task instance - Its callback dictionary
        """

        raise NotImplementedError

    def completed_callback(self, task: Task) -> Event:
        """Callback to call when the task has been completed

        Args:
            task (Task): completed task

        Returns:
            Event: Success event
        """

        return task.completed_callback()
