from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import override

from rich.progress import Progress

from fastrag.config.config import Resources
from fastrag.events import Event
from fastrag.helpers.experiments import Experiment
from fastrag.plugins import PluginBase
from fastrag.steps.logs import Loggable


@dataclass
class IStepCommon(Loggable, PluginBase, ABC):
    task_id: int
    resources: Resources = field(repr=False)
    progress: Progress = field(repr=False)
    experiment: Experiment | None = field(init=False, repr=False)

    @abstractmethod
    def calculate_total(self) -> int:
        """Calculates the number of tasks to perform by this step

        Returns:
            int: number of tasks to perform
        """

        raise NotImplementedError

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
