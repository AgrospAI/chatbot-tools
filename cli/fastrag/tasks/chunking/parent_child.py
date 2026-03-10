import asyncio
from dataclasses import InitVar, dataclass, field
from typing import ClassVar, Literal, override

import aiofiles
import orjson
import uuid6
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import MarkdownHeaderTextSplitter

from fastrag.cache.entry import CacheEntry
from fastrag.cache.filters import Filter, MetadataFilter
from fastrag.embeddings import IEmbeddings
from fastrag.events import Event
from fastrag.plugins import inject
from fastrag.serve.database import get_session, initialize_database
from fastrag.stores.parent_chunk_db import ParentStore
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

    model: IEmbeddings = field(init=False, repr=False, hash=False)
    _semaphore: asyncio.Semaphore = field(init=False, repr=False, hash=False)

    def __post_init__(self, url: str, model_name: str, api_key: str, max_concurrent: int):
        initialize_database()
        self.model = inject(
            IEmbeddings,
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
                "experiment": self.experiment_hash,
            },
        )

        entries_bytes = await entries.get_content()
        entries_list = orjson.loads(entries_bytes) if entries_bytes else []

        if getattr(self, "results", None) is None:
            self.results = []

        self.results.extend(entries_list)

        status: Literal["Cached", "Generated"] = "Cached" if existed else "Generated"
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

        parent_chunks = []
        child_chunks = []
        parent_docs = parent_splitter.split_text(text)

        for p_doc in parent_docs:
            headers = [p_doc.metadata.get(k, "") for k in ["header_1", "header_2"]]
            title_path = " > ".join(filter(None, headers))

            context_header = title_path
            if metadata["description"]:
                context_header += f"\nSummary: {metadata['description']}"

            parent_content = f"{context_header}\n\n{p_doc.page_content}"
            parent_id = str(uuid6.uuid6())

            final_metadata = {
                **metadata,
                **p_doc.metadata,
                "title_path": title_path,
            }

            parent_chunks.append(
                {
                    "chunk_id": parent_id,
                    "page_content": parent_content,
                    "metadata": final_metadata,
                    "parent_id": None,
                }
            )

            if "| ---" in p_doc.page_content or "```" in p_doc.page_content:
                child_chunks.append(
                    {
                        "chunk_id": str(uuid6.uuid6()),
                        "page_content": parent_content,
                        "metadata": {
                            **final_metadata,
                            "parent_id": parent_id,
                        },
                        "parent_id": parent_id,
                    }
                )

                continue

            try:
                child_splitter = SemanticChunker(
                    embeddings=self.model,
                    breakpoint_threshold_type="standard_deviation",
                    breakpoint_threshold_amount=1.2,
                )

                async with self._semaphore:
                    loop = asyncio.get_running_loop()
                    child_docs = await loop.run_in_executor(
                        None,
                        child_splitter.create_documents,
                        [p_doc.page_content],
                    )

            except Exception as e:
                child_docs = [p_doc]

            for i, c_doc in enumerate(child_docs):
                child_content = c_doc.page_content
                if title_path:
                    child_content = f"{title_path}\n{child_content}"

                child_chunks.append(
                    {
                        "chunk_id": str(uuid6.uuid6()),
                        "page_content": child_content,
                        "metadata": {
                            **final_metadata,
                            "child_index": i,
                            "parent_id": parent_id,
                        },
                        "parent_id": parent_id,
                    }
                )

        self._save_parents_to_db(parent_chunks)
        return orjson.dumps(child_chunks)

    async def _save_parents_to_db(self, parents: list[dict]):
        if not parents:
            return

        async with get_session() as session:
            parent_store = ParentStore(session)

            for parent in parents:
                parent_store.save_parents(
                    parent_id=uuid6.UUID(parent["chunk_id"]),
                    content=parent["page_content"],
                    doc_metadata=parent["metadata"],
                )
