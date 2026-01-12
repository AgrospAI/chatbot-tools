import json
import uuid
from dataclasses import dataclass, field
from functools import partial
from typing import AsyncGenerator, ClassVar, override

from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter

from fastrag.cache.entry import CacheEntry
from fastrag.cache.filters import MetadataFilter
from fastrag.events import Event
from fastrag.helpers.filters import Filter
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
        existed, cached = await self.cache.get_or_create(
            uri=f"{uri}.chunk.json",
            contents=partial(self.chunker_logic, uri, entry),
            metadata={
                "step": "chunking",
                "strategy": ParentChildChunker.supported,
            },
        )

        if existed:
            entries = json.loads(cached.content)
            object.__setattr__(self, "_chunked", len(entries))

        status = "Cached" if existed else "Generated"
        yield ChunkingEvent(
            ChunkingEvent.Type.PROGRESS, f"{status} {self._chunked} chunks for {uri}"
        )

    @override
    def completed_callback(self) -> Event:
        return ChunkingEvent(
            ChunkingEvent.Type.COMPLETED,
            f"Chunking finished. Total chunks: {self._chunked}",
        )

    def chunker_logic(self, uri: str, entry: CacheEntry) -> bytes:
        text = entry.path.read_text(encoding="utf-8")

        embed_model = HuggingFaceEmbeddings(model_name=self.embedding_model)
        parent_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
        )
        child_splitter = SemanticChunker(
            embeddings=embed_model, breakpoint_threshold_type="percentile"
        )

        all_chunks = []
        parent_docs = parent_splitter.split_text(text)

        for p_doc in parent_docs:
            headers = [p_doc.metadata.get(k, "") for k in ["Header 1", "Header 2", "Header 3"]]
            title_path = " > ".join(filter(None, headers))

            parent_content = (
                f"Context: {title_path}\n\n{p_doc.page_content}"
                if title_path
                else p_doc.page_content
            )
            parent_id = str(uuid.uuid4())

            all_chunks.append(
                {
                    "chunk_id": parent_id,
                    "content": parent_content,
                    "metadata": {
                        **p_doc.metadata,
                        "source": uri,
                        "chunk_type": "parent",
                        "title_path": title_path,
                    },
                    "level": "parent",
                    "parent_id": None,
                }
            )

            if "| ---" in p_doc.page_content or "```" in p_doc.page_content:
                all_chunks.append(
                    {
                        "chunk_id": str(uuid.uuid4()),
                        "content": parent_content,
                        "metadata": {
                            **p_doc.metadata,
                            "source": uri,
                            "chunk_type": "child",
                        },
                        "level": "child",
                        "parent_id": parent_id,
                    }
                )
                continue

            try:
                child_docs = child_splitter.create_documents([p_doc.page_content])
            except Exception:
                child_docs = [p_doc]

            for i, c_doc in enumerate(child_docs):
                child_content = c_doc.page_content
                if title_path and not child_content.startswith("Context:"):
                    child_content = f"Context: {title_path}\n{child_content}"

                all_chunks.append(
                    {
                        "chunk_id": str(uuid.uuid4()),
                        "content": child_content,
                        "metadata": {
                            **p_doc.metadata,
                            "source": uri,
                            "chunk_type": "child",
                            "child_index": i,
                        },
                        "level": "child",
                        "parent_id": parent_id,
                    }
                )

        object.__setattr__(self, "_chunked", len(all_chunks))
        return json.dumps(all_chunks).encode("utf-8")
