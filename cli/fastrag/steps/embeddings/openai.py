from dataclasses import dataclass
from typing import ClassVar, override

from fastrag.events import Event
from fastrag.helpers.filters import AndFilter, Filter
from fastrag.steps.embeddings.events import EmbeddingEvent
from fastrag.steps.task import Task


@dataclass(frozen=True)
class SelfHostedEmbeddings(Task):
    """Self-hosted OpenAI-compatible embedding model"""

    supported: ClassVar[list[str]] = ["OpenAI-Simple", "openai", "openai-simple"]
    filter: ClassVar[Filter] = AndFilter([])

    model: str
    api_key: str
    url: str

    @override
    async def callback(self, uri=None, entry=None):
        yield EmbeddingEvent(EmbeddingEvent.Type.PROGRESS, "TODO")
        return

    @override
    def completed_callback(self) -> Event:
        return EmbeddingEvent(EmbeddingEvent.Type.COMPLETED, "TODO")
