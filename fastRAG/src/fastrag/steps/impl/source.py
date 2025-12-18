from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Iterable, override

from fastrag.config.config import Source
from fastrag.plugins import PluginRegistry, plugin
from fastrag.steps.fetchers.events import FetchingEvent
from fastrag.steps.step import IStep
from fastrag.systems import System


@dataclass(frozen=True)
@plugin(system=System.STEP, supported="fetching")
class SourceStep(IStep):

    step: list[Source]
    description: ClassVar[str] = "FETCH"

    @override
    def get_tasks(self) -> Iterable[AsyncGenerator[FetchingEvent, None]]:
        return [
            PluginRegistry.get_instance(
                System.FETCHING,
                source.strategy,
                **source.params,
            ).fetch()
            for source in self.step
        ]

    @override
    def log_verbose(self, event: FetchingEvent) -> None:
        match event.type:
            case FetchingEvent.Type.PROGRESS:
                self.progress.log(event.data)
            case FetchingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case FetchingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
            case _:
                self.progress.log(f"[red]:?: UNEXPECTED EVENT: {event}[/red]")

    @override
    def log(self, event: FetchingEvent) -> None:
        match event.type:
            case FetchingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case FetchingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
            case _:
                self.progress.log(f"[red]:?: UNEXPECTED EVENT: {event}[/red]")
