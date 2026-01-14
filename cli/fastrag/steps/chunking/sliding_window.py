import json
import uuid
from dataclasses import dataclass, field
from functools import partial
from typing import AsyncGenerator, ClassVar, override

from langchain_text_splitters import RecursiveCharacterTextSplitter

from fastrag.cache.entry import CacheEntry
from fastrag.cache.filters import MetadataFilter
from fastrag.events import Event
from fastrag.helpers.filters import Filter
from fastrag.helpers.markdown_utils import clean_markdown, normalize_metadata
from fastrag.steps.task import Task


@dataclass(frozen=True)
class SlidingWindowChunker(Task):
    supported: ClassVar[str] = "SlidingWindow"
    filter: ClassVar[Filter] = MetadataFilter(step="parsing")

    chunk_size: int = 1000
    chunk_overlap: int = 200

    _chunked: int = field(default=0, init=False)
    _cached: bool = field(default=False, init=False)

    @override
    async def callback(
        self,
        uri: str,
        entry: CacheEntry,
    ) -> AsyncGenerator[Event, None]:
        existed, cached = await self.cache.get_or_create(
            uri=f"{entry.path.resolve().as_uri()}.sliding.json",
            contents=partial(self.chunker_logic, uri, entry),
            metadata={
                "step": "chunking",
                "strategy": SlidingWindowChunker.supported,
            },
        )

        if existed:
            entries = json.loads(cached.content)
            object.__setattr__(self, "_chunked", len(entries))
            object.__setattr__(self, "_cached", True)

        status = "Cached" if existed else "Generated"
        yield Event(Event.Type.PROGRESS, f"{status} {self._chunked} chunks for {uri}")

    @override
    def completed_callback(self) -> Event:
        status = f"Chunking done{' (cached)' if self._cached else ''}"
        return Event(
            Event.Type.COMPLETED,
            f"{status} {self._chunked} chunks",
        )

    def chunker_logic(self, uri: str, entry: CacheEntry) -> bytes:
        raw_text = entry.path.read_text(encoding="utf-8")

        text, raw_meta = clean_markdown(raw_text)
        metadata = normalize_metadata(raw_meta, uri)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            keep_separator=False,
        )

        all_chunks = []

        docs = splitter.create_documents([text], metadatas=[metadata])
        for i, doc in enumerate(docs):
            context_header = f"Document: {metadata['title']}"
            if metadata["description"]:
                context_header += f"\nSummary: {metadata['description']}"

            final_content = f"{context_header}\n\n{doc.page_content}"

            all_chunks.append(
                {
                    "chunk_id": str(uuid.uuid4()),
                    "content": final_content,
                    "metadata": {
                        **doc.metadata,
                        "chunk_index": i,
                        "chunk_type": "sliding_window",
                        "strategy": "recursive",
                    },
                    "level": "flat",
                }
            )

        object.__setattr__(self, "_chunked", len(all_chunks))
        return json.dumps(all_chunks).encode("utf-8")
