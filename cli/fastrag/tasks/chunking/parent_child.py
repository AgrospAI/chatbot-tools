import asyncio
import uuid
from dataclasses import InitVar, dataclass, field
from typing import ClassVar, override

import aiofiles
import orjson
from langchain_core.embeddings import Embeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import MarkdownHeaderTextSplitter

from fastrag.cache.entry import CacheEntry
from fastrag.cache.filters import Filter, MetadataFilter
from fastrag.events import Event
from fastrag.plugins import inject
from fastrag.tasks.base import Run, Task
from fastrag.tasks.chunking.markdown_utils import clean_markdown, normalize_metadata


@dataclass
class ParentChildChunker(Task):
    supported: ClassVar[str] = "ParentChild"
    filter: ClassVar[Filter] = MetadataFilter(step="parsing")

    url: InitVar[str]
    model_name: InitVar[str]
    api_key: InitVar[str]
    max_concurrent: InitVar[int] = 5

    model: Embeddings = field(init=False, repr=False, hash=False)
    _semaphore: asyncio.Semaphore = field(init=False, repr=False, hash=False)

    def __post_init__(self, url: str, model_name: str, api_key: str, max_concurrent: int):
        self.model = inject(
            Embeddings,
            "openai-simple",
            url=url,
            model=model_name,
            api_key=api_key,
        )
        self._semaphore = asyncio.Semaphore(max_concurrent)

    @override
    async def run(self, uri: str, entry: CacheEntry) -> Run:
        existed, entries = await self.cache.get_or_create(
            uri=f"{entry.path.resolve().as_uri()}.{self.__class__.__name__}.{self.model.__class__.__name__}.chunk.jsonl",
            contents=lambda: self.chunker_logic(uri, entry),
            metadata={
                "step": "chunking",
                "strategy": ParentChildChunker.supported,
                "experiment": self.experiment.hash,
            },
        )

        entries_bytes = await entries.get_content()
        entries_list = orjson.loads(entries_bytes) if entries_bytes else []

        if getattr(self, "results", None) is None:
            self.results = []

        self.results.extend(entries_list)

        status = "Cached" if existed else "Generated"
        yield Event(
            Event.Type.PROGRESS,
            f"{self.__class__.__name__} {status} {len(entries_list)} chunks for {entry.path}",
        )

    @override
    def completed_callback(self) -> Event:
        return Event(Event.Type.COMPLETED, "Finished ParentChildChunking")

    async def chunker_logic(self, uri: str, entry: CacheEntry) -> bytes:
        async with aiofiles.open(entry.path) as f:
            raw_text = await f.read()

        text, raw_metadata = clean_markdown(raw_text)
        metadata = normalize_metadata(raw_metadata, uri)

        parent_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[("#", "header_1"), ("##", "header_2")]
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
                    "page_content": parent_content,
                    "metadata": final_metadata,
                    "level": "parent",
                    "parent_id": None,
                }
            )

            if "| ---" in p_doc.page_content or "```" in p_doc.page_content:
                all_chunks.append(
                    {
                        "chunk_id": str(uuid.uuid4()),
                        "page_content": parent_content,
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
                child_splitter = SemanticChunker(
                    embeddings=self.model,
                    breakpoint_threshold_type="percentile",
                )

                async with self._semaphore:
                    loop = asyncio.get_running_loop()
                    child_docs = await loop.run_in_executor(
                        None,
                        child_splitter.create_documents,
                        [p_doc.page_content],
                    )

            except Exception:
                child_docs = [p_doc]

            for i, c_doc in enumerate(child_docs):
                child_content = c_doc.page_content
                if title_path and not child_content.startswith("Context:"):
                    child_content = f"Context: {title_path}\n{child_content}"

                all_chunks.append(
                    {
                        "chunk_id": str(uuid.uuid4()),
                        "page_content": child_content,
                        "metadata": {
                            **final_metadata,
                            "chunk_type": "child",
                            "child_index": i,
                        },
                        "level": "child",
                        "parent_id": parent_id,
                    }
                )

        return orjson.dumps(all_chunks)
