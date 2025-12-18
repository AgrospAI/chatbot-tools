from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, List, override

from fastrag.config.config import Chunking
from fastrag.events import Event
from fastrag.plugins import plugin
from fastrag.steps.chunking import ChunkingEvent
from fastrag.steps.step import IStep
from fastrag.systems import System


@dataclass(frozen=True)
@plugin(system=System.STEP, supported="chunking")
class ChunkingStep(IStep):

    step: list[Chunking]
    description: ClassVar[str] = "CHUNK"

    @override
    def get_tasks(self) -> List[AsyncGenerator[Event, None]]:
        return []

    @override
    def log_verbose(self, event: ChunkingEvent) -> None:
        match event.type:
            case ChunkingEvent.Type.PROGRESS:
                self.progress.log(event.data)
            case ChunkingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case ChunkingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
            case _:
                self.progress.log(f"[red]:?: UNEXPECTED EVENT: {event}[/red]")

    @override
    def log(self, event: ChunkingEvent) -> None:
        match event.type:
            case ChunkingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case ChunkingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
            case _:
                self.progress.log(f"[red]:?: UNEXPECTED EVENT: {event}[/red]")
