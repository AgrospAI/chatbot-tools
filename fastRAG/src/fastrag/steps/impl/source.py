from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Iterable, override

from fastrag.config.config import Source
from fastrag.fetchers.events import FetchingEvent
from fastrag.plugins.base import PluginRegistry, plugin
from fastrag.steps.impl.arunner import IAsyncStepRunner


@dataclass(frozen=True)
@plugin(key="step", supported="fetching")
class SourceStep(IAsyncStepRunner):

    step: list[Source]
    description: ClassVar[str] = "FETCH"

    @override
    def get_tasks(self) -> Iterable[AsyncGenerator[FetchingEvent, None]]:
        return [
            PluginRegistry.get("fetching", source.strategy)(**source.params).fetch()
            for source in self.step
        ]

    @override
    def _log_verbose(self, event: FetchingEvent) -> None:
        match event.type:
            case FetchingEvent.Type.PROGRESS:
                self.progress.log(event.data)
            case FetchingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case FetchingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")

    @override
    def _log(self, event: FetchingEvent) -> None:
        match event.type:
            case FetchingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case FetchingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
