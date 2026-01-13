from dataclasses import dataclass, field
from typing import ClassVar, override

from fastrag.cache.filters import MetadataFilter
from fastrag.events import Event
from fastrag.helpers.filters import Filter
from fastrag.steps.task import Task


@dataclass(frozen=True)
class SelfHostedEmbeddings(Task):
    """Self-hosted OpenAI-compatible embedding model"""

    supported: ClassVar[list[str]] = ["OpenAI-Simple", "openai", "openai-simple"]
    filter: ClassVar[Filter] = MetadataFilter(step="chunking")

    model: str = field()
    api_key: str = field(repr=False)
    url: str = field()

    @override
    async def run(self, uri=None, entry=None):
        yield Event(Event.Type.PROGRESS, f"Embedding {uri} TODO")
        self._set_results([])
        return

    @override
    def completed_callback(self) -> Event:
        return Event(Event.Type.COMPLETED, "Embedding completed TODO")
