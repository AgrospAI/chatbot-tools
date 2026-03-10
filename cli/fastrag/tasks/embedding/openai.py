from dataclasses import InitVar, dataclass, field
from typing import ClassVar, Sequence, override

import orjson

from fastrag.cache.entry import CacheEntry
from fastrag.cache.filters import Filter, MetadataFilter
from fastrag.embeddings import IEmbeddings
from fastrag.events import Event
from fastrag.plugins import inject
from fastrag.stores.store import Document
from fastrag.tasks.base import Run, Task


@dataclass(kw_only=True)
class OpenAISimple(Task):
    supported: ClassVar[list[str]] = ["OpenAI-Simple", "openai-simple"]
    filter: ClassVar[Filter] = MetadataFilter(step="chunking")

    api_key: InitVar[str]
    url: InitVar[str]
    batch_size: InitVar[int] = 1

    model: str
    embedder: IEmbeddings = field(init=False)

    def __post_init__(self, api_key: str, url: str, batch_size: int):
        self.embedder = inject(
            IEmbeddings,
            "OpenAI-Simple",
            model=self.model,
            api_key=api_key,
            url=url,
            batch_size=batch_size,
        )

    @override
    async def run(self, uri: str, entry: CacheEntry) -> Run:
        existed, cached = await self.cache.get_or_create(
            uri=f"{entry.path.resolve().as_uri()}.{self.__class__.__name__}.{self.model}.embedding.json",
            contents=lambda: self.embedding_logic(entry),
            metadata={"step": "embedding", "experiment": self.experiment_hash},
        )

        data = orjson.loads(await cached.get_content())
        if existed and data:
            vectors = []
            documents = []
            for chunk in (chunk for chunk in data if chunk["page_content"]):
                vectors.append(chunk.pop("vector"))
                documents.append(Document(**chunk))

            await self.upload_embeddings(documents, vectors)
            yield Event(
                Event.Type.PROGRESS,
                f"Re-uploaded embeddings to {self.experiment_hash}",
            )

        self.results = data

        status = "Cached" if existed else "Generated"
        yield Event(
            Event.Type.PROGRESS,
            f"{self.__class__.__name__} {self.experiment_hash} {status} embeddings for {uri}",
        )

    @override
    def completed_callback(self) -> Event:
        return Event(Event.Type.COMPLETED, f"Completed {self.__class__.__name__}")

    async def embedding_logic(self, entry: CacheEntry) -> bytes:
        raw_json = entry.path.read_text(encoding="utf-8")
        chunks = orjson.loads(raw_json)

        if not chunks:
            return orjson.dumps([])

        documents = [Document(**chunk) for chunk in chunks]

        total_vectors = await self.embedder.embed_documents(
            [chunk["page_content"] for chunk in chunks]
        )

        await self.upload_embeddings(documents, total_vectors)

        for i, chunk in enumerate(chunks):
            chunk["vector"] = total_vectors[i]

        return orjson.dumps(chunks)

    async def upload_embeddings(
        self,
        documents: Sequence[Document],
        embeddings: list[list[float]],
    ) -> None:
        await self.store.add_documents(
            documents,
            embeddings,
            self.experiment_hash,
        )
