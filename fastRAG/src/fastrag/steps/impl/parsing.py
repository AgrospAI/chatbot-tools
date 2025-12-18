from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Iterable, override

from fastrag.config.config import Parsing
from fastrag.plugins import PluginRegistry, plugin
from fastrag.steps.parsing.events import ParsingEvent
from fastrag.steps.step import IStep
from fastrag.systems import System


@dataclass(frozen=True)
@plugin(system=System.STEP, supported="parsing")
class ParsingStep(IStep):

    step: list[Parsing]
    description: ClassVar[str] = "PARSE"

    @override
    def get_tasks(self) -> Iterable[AsyncGenerator[ParsingEvent, None]]:
        return [
            PluginRegistry.get_instance(
                System.PARSING,
                source.strategy,
                use=source.use,
            ).parse()
            for source in self.step
        ]

    @override
    def log_verbose(self, event: ParsingEvent) -> None:
        match event.type:
            case ParsingEvent.Type.PROGRESS:
                self.progress.log(event.data)
            case ParsingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case ParsingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
            case _:
                self.progress.log(f"[red]:?: UNEXPECTED EVENT: {event}[/red]")

    @override
    def log(self, event: ParsingEvent) -> None:
        match event.type:
            case ParsingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case ParsingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
            case _:
                self.progress.log(f"[red]:?: UNEXPECTED EVENT: {event}[/red]")
