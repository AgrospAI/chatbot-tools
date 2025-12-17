from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Iterable, override

from fastrag.config.config import Embedding
from fastrag.embeddings import EmbeddingEvent
from fastrag.plugins.base import plugin
from fastrag.steps.impl.arunner import IAsyncStepRunner


@dataclass(frozen=True)
@plugin(key="step", supported="embedding")
class EmbeddingStep(IAsyncStepRunner):

    step: list[Embedding]
    description: ClassVar[str] = "EMBED"

    @override
    def get_tasks(self) -> Iterable[AsyncGenerator[EmbeddingEvent, None]]:
        # TODO: Fill with asyncio task calls
        return []

    @override
    def _log_verbose(self, event: EmbeddingEvent) -> None:
        match event.type:
            case EmbeddingEvent.Type.PROGRESS:
                self.progress.log(event.data)
            case EmbeddingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case EmbeddingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")

    @override
    def _log(self, event: EmbeddingEvent) -> None:
        match event.type:
            case EmbeddingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case EmbeddingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
