from dataclasses import dataclass
from typing import AsyncIterable, ClassVar, Iterable, Mapping, override

from fastrag.config.config import Embedding
from fastrag.embeddings.events import EmbeddingEvent
from fastrag.steps.impl.arunner import IAsyncStepRunner


@dataclass(frozen=True)
class EmbeddingStep(IAsyncStepRunner):

    step: list[Embedding]
    description: ClassVar[str] = "Embedding chunks"

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["embedding"]

    @override
    def get_tasks(self) -> Mapping[int, AsyncIterable]:
        return []

    @override
    def callback(self, event: EmbeddingEvent) -> None:
        match event.type:
            case EmbeddingEvent.Type.PROGRESS:
                self.progress.log(event.data)
            case EmbeddingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case EmbeddingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]{event.data}[/red]")
