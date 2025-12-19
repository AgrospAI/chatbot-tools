from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Dict, override

from fastrag.cache.cache import ICache
from fastrag.config.config import Embedding
from fastrag.events import Event
from fastrag.plugins import plugin
from fastrag.steps.embeddings import EmbeddingEvent
from fastrag.steps.step import IStep
from fastrag.steps.task import Task
from fastrag.systems import System


@dataclass
@plugin(system=System.STEP, supported="embedding")
class EmbeddingStep(IStep):

    step: list[Embedding]
    description: ClassVar[str] = "EMBED"

    @override
    async def get_tasks(self, cache: ICache) -> Dict[Task, AsyncGenerator[Event, None]]:
        return {}

    @override
    def log_verbose(self, event: EmbeddingEvent) -> None:
        match event.type:
            case EmbeddingEvent.Type.PROGRESS:
                self.progress.log(event.data)
            case EmbeddingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case EmbeddingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
            case _:
                self.progress.log(f"[red]:?: UNEXPECTED EVENT: {event}[/red]")

    @override
    def log_normal(self, event: EmbeddingEvent) -> None:
        match event.type:
            case EmbeddingEvent.Type.PROGRESS:
                ...
            case _:
                self.log_verbose(event)
