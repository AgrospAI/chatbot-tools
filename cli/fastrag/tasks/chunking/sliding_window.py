import asyncio
from dataclasses import dataclass
from typing import ClassVar, override

import aiofiles
import orjson
import uuid6
from langchain_text_splitters import RecursiveCharacterTextSplitter

from fastrag.cache.entry import CacheEntry
from fastrag.cache.filters import Filter, MetadataFilter
from fastrag.events import Event
from fastrag.tasks.base import Run, Task
from fastrag.tasks.chunking.markdown_utils import clean_markdown, normalize_metadata


@dataclass
class SlidingWindowChunker(Task):
    supported: ClassVar[str] = "SlidingWindow"
    filter: ClassVar[Filter] = MetadataFilter(step="parsing")

    chunk_size: int = 1200
    chunk_overlap: int = 200

    @override
    async def run(self, uri: str, entry: CacheEntry) -> Run:
        existed, entries = await self.cache.get_or_create(
            uri=f"{entry.path.resolve().as_uri()}.{self.__class__.__name__}.chunk.json",
            contents=lambda: self.chunker_logic(uri, entry),
            metadata={
                "step": "chunking",
                "strategy": "SlidingWindow",
                "size": self.chunk_size,
                "overlap": self.chunk_overlap,
                "experiment": self.experiment.hash,
            },
        )

        content = await entries.get_content()
        data = orjson.loads(content)

        if getattr(self, "results", None) is None:
            self.results = []

        self.results.extend(data)

        status = "Cached" if existed else "Generated"
        yield Event(
            Event.Type.PROGRESS,
            f"{self.__class__.__name__} {status} {len(data)} chunks for {entry.path}",
        )

    @override
    def completed_callback(self) -> Event:
        return Event(Event.Type.COMPLETED, "Finished SlidingWindow")

    async def chunker_logic(self, uri: str, entry: CacheEntry) -> bytes:
        async with aiofiles.open(entry.path, "r") as f:
            raw_text = await f.read()

        text, raw_metadata = clean_markdown(raw_text)
        metadata = normalize_metadata(raw_metadata, uri)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        docs = splitter.create_documents([text])

        loop = asyncio.get_running_loop()
        docs = await loop.run_in_executor(None, splitter.create_documents, [text])

        all_chunks = []

        for i, doc in enumerate(docs):
            chunk_content = doc.page_content

            if metadata.get("title"):
                chunk_content = f"{metadata['title']}\n{chunk_content}"

            all_chunks.append(
                {
                    "chunk_id": str(uuid6.uuid6()),
                    "page_content": chunk_content,
                    "metadata": {**metadata, "chunk_index": i},
                }
            )

        return orjson.dumps(all_chunks)
