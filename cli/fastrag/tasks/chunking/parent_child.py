import json
import uuid
from dataclasses import InitVar, dataclass, field
from typing import ClassVar, override

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

    model: Embeddings = field(init=False, repr=False, hash=False)

    def __post_init__(self, url: str, model_name: str, api_key: str) -> None:
        self.model = inject(
            Embeddings,
            "openai-simple",
            url=url,
            model=model_name,
            api_key=api_key,
        )

    @override
    async def run(self, uri: str, entry: CacheEntry) -> Run:
        existed, entries = await self.cache.get_or_create(
            uri=f"{entry.path.resolve().as_uri()}.{self.__class__.__name__}.{self.model.__class__.__name__}.chunk.json",
            contents=lambda: self.chunker_logic(uri, entry),
            metadata={
                "step": "chunking",
                "strategy": ParentChildChunker.supported,
                "experiment": self.experiment.hash,
            },
        )

        entries = json.loads(entries.content)

        if getattr(self, "results", None) is None:
            self.results = []

        self.results.extend(entries)

        status = "Cached" if existed else "Generated"
        yield Event(
            Event.Type.PROGRESS,
            f"{self.__class__.__name__} {status} {len(entries)} chunks for {entry.path}",
        )

    @override
    def completed_callback(self) -> Event:
        return Event(Event.Type.COMPLETED, "Finished ParentChildChunking")

    async def chunker_logic(self, uri: str, entry: CacheEntry) -> bytes:
        raw_text = entry.path.read_text(encoding="utf-8")
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

        return json.dumps(all_chunks).encode("utf-8")
