from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, override

from rich.progress import Progress

from fastrag.cache.cache import ICache
from fastrag.config.config import Step, Steps
from fastrag.events import Event
from fastrag.plugins import PluginBase
from fastrag.steps.logs import Loggable
from fastrag.steps.task import Task


@dataclass
class IStep(Loggable, PluginBase, ABC):
    step: Step
    progress: Progress
    task_id: int
    description: ClassVar[str] = "UNKNOWN STEP"
    _tasks: ClassVar[dict[Task, list[AsyncGenerator[Event, None]]]] = None

    def calculate_total(self) -> int:
        """Calculates the number of tasks to perform by this step

        Returns:
            int: number of tasks to perform
        """
        return len(self.step) if self.step else 0

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
    async def get_tasks(
        self, cache: ICache
    ) -> AsyncGenerator[tuple[Task, list[AsyncGenerator[Event, None]]], None]:
        """Generate a dict with the tasks to perform

        Returns:
            dict[Task, list[AsyncGenerator[Event, None]]]: Task instance - Its list of callbacks
        """

        raise NotImplementedError


@dataclass
class IMultiStep(IStep):
    step: Steps

    @abstractmethod
    def get_steps(self) -> list[IStep]:
        """Get the instances of the involved steps

        Returns:
            list[IStep]: list of instances
        """

        raise NotImplementedError
