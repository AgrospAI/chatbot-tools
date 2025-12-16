from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Iterable, override

from fastrag.config.config import Embedding
from fastrag.embeddings import EmbeddingEvent
from fastrag.steps.impl.arunner import IAsyncStepRunner


@dataclass(frozen=True)
class EmbeddingStep(IAsyncStepRunner):

    step: list[Embedding]
    description: ClassVar[str] = "EMBED"

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["embedding"]

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
