import json
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import AsyncGenerator, ClassVar, override

from fastrag.cache.entry import CacheEntry
from fastrag.cache.filters import StepFilter
from fastrag.events import Event
from fastrag.helpers.filters import Filter
from fastrag.steps.task import Task


def chunk_md(path: Path, chunk_size: int) -> list[str]:
    """A simple markdown chunker that splits by paragraphs."""
    text = path.read_text(encoding="utf-8")
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current_chunk = ""
    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 2 <= chunk_size:
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = paragraph

    return json.dumps({"chunks": chunks}).encode("utf-8")


@dataclass(frozen=True)
class RecursiveChunker(Task):
    supported: ClassVar[str] = "RecursiveChunker"
    filter: ClassVar[Filter] = StepFilter("parsing")

    chunk_size: int = field(default=500)

    @override
    async def callback(
        self,
        uri: str,
        entry: CacheEntry,
    ) -> AsyncGenerator[Event, None]:
        existed, _ = await self.cache.get_or_create(
            uri=f"{entry.path.resolve().as_uri()}.{self.__class__.__name__}.{self.chunk_size}.chunk.json",
            contents=partial(chunk_md, entry.path, self.chunk_size),
            step="chunking",
            metadata={
                "source": uri,
                "strategy": RecursiveChunker.supported,
                "experiment": self.experiment.hash,
            },
        )

        yield Event(
            Event.Type.PROGRESS,
            ("Cached" if existed else "Chunking") + f" Markdown {uri}",
        )

    @override
    def completed_callback(self) -> Event:
        return Event(
            Event.Type.COMPLETED,
            "Chunked Markdown documents with RecursiveChunker",
        )
