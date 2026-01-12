import json
from dataclasses import dataclass, field
from functools import partial
from typing import AsyncGenerator, ClassVar, override

from fastrag.cache.entry import CacheEntry
from fastrag.cache.filters import MetadataFilter
from fastrag.events import Event
from fastrag.helpers.filters import Filter
from fastrag.steps.chunking.chunker_logic import chunker_logic
from fastrag.steps.chunking.events import ChunkingEvent
from fastrag.steps.task import Task


@dataclass(frozen=True)
class ParentChildChunker(Task):
    supported: ClassVar[str] = "ParentChild"
    filter: ClassVar[Filter] = MetadataFilter(step="parsing")

    chunk_size: int = 500
    embedding_model: str = "all-MiniLM-L6-v2"

    _chunked: int = field(default=0, init=False)

    @override
    async def callback(
        self,
        uri: str,
        entry: CacheEntry,
    ) -> AsyncGenerator[ChunkingEvent, None]:
        markdown_text = entry.path.read_text(encoding="utf-8")

        existed, result_entry = await self.cache.get_or_create(
            uri=f"{uri}.chunks.json",
            contents=partial(chunker_logic, markdown_text, uri, self.embedding_model),
            metadata={
                "step": "chunking",
                "source": uri,
                "strategy": ParentChildChunker.supported,
            },
        )

        chunks_data = json.loads(result_entry.path.read_text())

        new_count = self._chunked + len(chunks_data)
        object.__setattr__(self, "_chunked", new_count)

        status = "Cached" if existed else "Generated"
        yield ChunkingEvent(
            ChunkingEvent.Type.PROGRESS, f"{status} {len(chunks_data)} chunks for {uri}"
        )

    @override
    def completed_callback(self) -> Event:
        return ChunkingEvent(
            ChunkingEvent.Type.COMPLETED,
            f"Chunking finished. Total chunks: {self._chunked}",
        )
