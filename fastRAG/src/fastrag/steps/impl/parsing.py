from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Iterable, override

from fastrag.config.config import Parsing
from fastrag.parsing.events import ParsingEvent
from fastrag.plugins.base import PluginRegistry, plugin
from fastrag.steps.impl.arunner import IAsyncStepRunner


@dataclass(frozen=True)
@plugin(key="step", supported="parsing")
class ParsingStep(IAsyncStepRunner):

    step: list[Parsing]
    description: ClassVar[str] = "PARSE"

    @override
    def get_tasks(self) -> Iterable[AsyncGenerator[ParsingEvent, None]]:
        return [
            PluginRegistry.get("parsing", source.strategy)(source.use).parse()
            for source in self.step
        ]

    @override
    def _log_verbose(self, event: ParsingEvent) -> None:
        match event.type:
            case ParsingEvent.Type.PROGRESS:
                self.progress.log(event.data)
            case ParsingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case ParsingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")

    @override
    def _log(self, event: ParsingEvent) -> None:
        match event.type:
            case ParsingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case ParsingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
