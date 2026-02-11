from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, ClassVar, override

from rich.progress import Progress

from fastrag.events import Event
from fastrag.plugins import PluginBase


@dataclass
class Loggable(PluginBase, ABC):
    log: Callable[[Event], None] = field(init=False, repr=False)

    is_verbose: ClassVar[bool] = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "log", self.log_verbose if Loggable.is_verbose else self.log_normal
        )

    @abstractmethod
    def log_normal(self, event: Event) -> None:
        """Log the given event. Not verbose.

        Args:
            event (Event): step event
        """

        raise NotImplementedError

    @abstractmethod
    def log_verbose(self, event: Event) -> None:
        """Verbose log the given event.

        Args:
            event (Event): step event
        """

        raise NotImplementedError


@dataclass
class Logger(Loggable):
    supported: ClassVar[str] = "rich"

    progress: Progress

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
