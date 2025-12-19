from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Dict, override

from fastrag.cache.cache import ICache
from fastrag.config.config import Chunking
from fastrag.events import Event
from fastrag.plugins import plugin
from fastrag.steps.chunking import ChunkingEvent
from fastrag.steps.step import IStep
from fastrag.steps.task import Task
from fastrag.systems import System


@dataclass
@plugin(system=System.STEP, supported="chunking")
class ChunkingStep(IStep):

    step: list[Chunking]
    description: ClassVar[str] = "CHUNK"

    @override
    async def get_tasks(self, cache: ICache) -> Dict[Task, AsyncGenerator[Event, None]]:
        return {}

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
    def log_normal(self, event: ChunkingEvent) -> None:
        match event.type:
            case ChunkingEvent.Type.PROGRESS:
                ...
            case ChunkingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case ChunkingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
            case _:
                self.progress.log(f"[red]:?: UNEXPECTED EVENT: {event}[/red]")
