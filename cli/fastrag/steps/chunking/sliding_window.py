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

    chunk_size: int = 1200
    chunk_overlap: int = 200 

    _chunked: int = field(default=0, init=False, repr=False)
    _cached: bool = field(default=False, init=False)

    @override
    async def run(
        self,
        uri: str,
        entry: CacheEntry,
    ) -> AsyncGenerator[Event, None]:
        existed, entries = await self.cache.get_or_create(
            uri=f"{entry.path.resolve().as_uri()}.chunk.json",
            contents=partial(self.chunker_logic, uri, entry),
            metadata={
                "step": "chunking",
                "strategy": "SlidingWindow",
                "size": self.chunk_size,
                "overlap": self.chunk_overlap
            },
        )

        data = json.loads(entries.content)

        if not self.results:
            self._set_results([])

        self._results.append(data)
        object.__setattr__(self, "_chunked", len(data))

        status = "Cached" if existed else "Generated"
        yield Event(Event.Type.PROGRESS, f"{status} {len(data)} chunks for {entry.path}")

    @override
    def completed_callback(self) -> Event:
        return Event(Event.Type.COMPLETED, f"Finished SlidingWindow: {self._chunked} chunks")

    def chunker_logic(self, uri: str, entry: CacheEntry) -> bytes:
        raw_text = entry.path.read_text(encoding="utf-8")
        text, raw_metadata = clean_markdown(raw_text)
        metadata = normalize_metadata(raw_metadata, uri)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        docs = splitter.create_documents([text])
        all_chunks = []

        for i, doc in enumerate(docs):
            chunk_content = doc.page_content
            
            if metadata.get("title"):
                chunk_content = f"Context: {metadata['title']}\n{chunk_content}"

            all_chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "page_content": chunk_content,
                "metadata": {
                    **metadata,
                    "chunk_index": i,
                    "total_chunks": len(docs)
                },
                "level": "child",
                "parent_id": None
            })

        return json.dumps(all_chunks).encode("utf-8")
