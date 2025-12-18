from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Iterable, override

from fastrag.config.config import Embedding
from fastrag.plugins import plugin
from fastrag.steps.embeddings import EmbeddingEvent
from fastrag.steps.step import IStep
from fastrag.systems import System


@dataclass(frozen=True)
@plugin(system=System.STEP, supported="embedding")
class EmbeddingStep(IStep):

    step: list[Embedding]
    description: ClassVar[str] = "EMBED"

    @override
    def get_tasks(self) -> Iterable[AsyncGenerator[EmbeddingEvent, None]]:
        # TODO: Fill with asyncio task calls
        return []

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
    def log(self, event: EmbeddingEvent) -> None:
        match event.type:
            case EmbeddingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case EmbeddingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
            case _:
                self.progress.log(f"[red]:?: UNEXPECTED EVENT: {event}[/red]")
