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
from fastrag.helpers.markdown_utils import clean_markdown, normalize_metadata
from fastrag.steps.task import Task


@dataclass(frozen=True)
class ParentChildChunker(Task):
    supported: ClassVar[str] = "ParentChild"
    filter: ClassVar[Filter] = MetadataFilter(step="parsing")

    chunk_size: int = 500
    embedding_model: str = "all-MiniLM-L6-v2"

    _chunked: int = field(default=0, init=False, repr=False)
    _cached: bool = field(default=False, init=False, repr=False)

    @override
    async def run(
        self,
        uri: str,
        entry: CacheEntry,
    ) -> AsyncGenerator[Event, None]:
        existed, entries = await self.cache.get_or_create(
            uri=f"{entry.path}.chunk.json",
            contents=partial(self.chunker_logic, uri, entry),
            metadata={
                "step": "chunking",
                "strategy": ParentChildChunker.supported,
            },
        )

        if existed:
            object.__setattr__(self, "_cached", True)

        entries = json.loads(entries.content)

        if not self.results:
            self._set_results([])

        object.__setattr__(self, "_chunked", len(entries))
        self._results.append(entries)

        status = "Cached" if existed else "Generated"
        yield Event(Event.Type.PROGRESS, f"{status} {self._chunked} chunks for {entry.path}")

    @override
    def completed_callback(self) -> Event:
        status = f"Chunking done{' (cached)' if self._cached else ''}"
        return Event(
            Event.Type.COMPLETED,
            f"{status} {self._chunked} chunks",
        )

    def chunker_logic(self, uri: str, entry: CacheEntry) -> bytes:
        raw_text = entry.path.read_text(encoding="utf-8")
        text, raw_metadata = clean_markdown(raw_text)
        metadata = normalize_metadata(raw_metadata, uri)

        embed_model = HuggingFaceEmbeddings(model_name=self.embedding_model)
        parent_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[("#", "header_1"), ("##", "header_2"), ("###", "header_3")]
        )
        child_splitter = SemanticChunker(
            embeddings=embed_model, breakpoint_threshold_type="percentile"
        )

        all_chunks = []
        parent_docs = parent_splitter.split_text(text)

        for p_doc in parent_docs:
            headers = [p_doc.metadata.get(k, "") for k in ["header_1", "header_2", "header_3"]]
            title_path = " > ".join(filter(None, headers))

            context_header = f"Context: {title_path}"
            if metadata["description"]:
                context_header += f"\nSummary: {metadata['description']}"

            parent_content = f"{context_header}\n\n{p_doc.page_content}"
            parent_id = str(uuid.uuid4())

            final_metadata = {
                **metadata,
                **p_doc.metadata,
                "chunk_type": "parent",
                "title_path": title_path,
            }

            all_chunks.append(
                {
                    "chunk_id": parent_id,
                    "content": parent_content,
                    "metadata": final_metadata,
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
                            **final_metadata,
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
                            **final_metadata,
                            "chunk_type": "child",
                            "child_index": i,
                        },
                        "level": "child",
                        "parent_id": parent_id,
                    }
                )

        object.__setattr__(self, "_chunked", len(all_chunks))
        return json.dumps(all_chunks).encode("utf-8")
