from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Dict, List, override

from fastrag.cache.cache import ICache
from fastrag.config.config import Parsing
from fastrag.events import Event
from fastrag.plugins import PluginRegistry, plugin
from fastrag.steps.parsing.events import ParsingEvent
from fastrag.steps.step import IStep
from fastrag.steps.task import Task
from fastrag.systems import System


@dataclass
@plugin(system=System.STEP, supported="parsing")
class ParsingStep(IStep):

    step: list[Parsing]
    description: ClassVar[str] = "PARSE"

    @override
    async def get_tasks(self, cache: ICache) -> Dict[Task, AsyncGenerator[Event, None]]:
        instances = [
            PluginRegistry.get_instance(
                System.PARSING, source.strategy, cache=cache, use=source.use
            )
            for source in self.step
        ]
        return {inst: inst.callback() for inst in instances}

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
    def log_normal(self, event: ParsingEvent) -> None:
        match event.type:
            case ParsingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case ParsingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
            case _:
                self.progress.log(f"[red]:?: UNEXPECTED EVENT: {event}[/red]")
