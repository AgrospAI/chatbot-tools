from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Dict, List, override

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
    description: ClassVar[str] = "UNKNOWN STEP"
    _tasks: ClassVar[Dict[Task, List[AsyncGenerator[Event, None]]]] = None

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

    async def tasks(self) -> Dict[Task, List[AsyncGenerator[Event, None]]]:
        if self._tasks is None:
            cache = get_constants().cache
            self._tasks = await self.get_tasks(cache)
        return self._tasks

    def completed_callback(self, task: Task) -> Event:
        """Callback to call when the task has been completed

        Args:
            task (Task): completed task

        Returns:
            Event: Success event
        """

        return task.completed_callback()

    @override
    def log_verbose(self, event: Event) -> None:
        match event.type:
            case Event.Type.PROGRESS:
                self.progress.log(event.data)
            case Event.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case Event.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
            case _:
                self.progress.log(f"[red]:?: UNEXPECTED EVENT: {event}[/red]")

    @override
    def log_normal(self, event: Event) -> None:
        match event.type:
            case Event.Type.PROGRESS:
                ...
            case _:
                self.log_verbose(event)

    @abstractmethod
    async def get_tasks(self, cache: ICache) -> Dict[Task, List[AsyncGenerator[Event, None]]]:
        """Generate a dict with the tasks to perform

        Returns:
            Dict[Task, List[AsyncGenerator[Event, None]]]: Task instance - Its list of callbacks
        """

        raise NotImplementedError
