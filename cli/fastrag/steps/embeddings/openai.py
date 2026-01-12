from dataclasses import dataclass
from typing import ClassVar, override

from fastrag.cache.filters import MetadataFilter
from fastrag.events import Event
from fastrag.helpers.filters import Filter
from fastrag.steps.embeddings.events import EmbeddingEvent
from fastrag.steps.task import Task


@dataclass(frozen=True)
class SelfHostedEmbeddings(Task):
    """Self-hosted OpenAI-compatible embedding model"""

    supported: ClassVar[list[str]] = ["OpenAI-Simple", "openai", "openai-simple"]
    filter: ClassVar[Filter] = MetadataFilter(step="chunking")

    model: str
    api_key: str
    url: str

    @override
    async def callback(self, uri=None, entry=None):
        yield EmbeddingEvent(EmbeddingEvent.Type.PROGRESS, f"Embedding {uri} TODO")
        return

    @override
    def completed_callback(self) -> Event:
        return EmbeddingEvent(EmbeddingEvent.Type.COMPLETED, "Embedding completed TODO")
