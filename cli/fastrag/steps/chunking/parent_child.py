from dataclasses import dataclass, field
from typing import AsyncGenerator, override

from httpx import AsyncClient

from fastrag.events import Event
from fastrag.helpers import URLField
from fastrag.plugins import plugin
from fastrag.steps.chunking.events import ChunkingEvent
from fastrag.steps.task import Task
from fastrag.systems import System

from langchain_core.embeddings import Embeddings


@dataclass(frozen=True)
@plugin(system=System.CHUNKING, supported="ParentChild")
class ParentChildChunker(Task):
    filter: ClassVar[Filter] = StepFilter("parsing")
    
    embedding_model: Embeddings
    parent_splitter
    child_splitter 

    _chunked : int = field(default=0, compare=False)    

    @override
    async def callback(
        self,
        uri: str,
        entry: CacheEntry,
    ) -> AsyncGenerator[ChunkingEvent, None]:
        ...

    @override
    def completed_callback(self) -> Event:
        return ChunkingEvent(
            ChunkingEvent.Type.COMPLETED,
            f"Created {self._chunked} chunks using ParentChildChunker",
        )