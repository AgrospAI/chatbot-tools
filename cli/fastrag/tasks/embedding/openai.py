import json
from dataclasses import InitVar, dataclass
from typing import ClassVar, override

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from fastrag.cache.entry import CacheEntry
from fastrag.cache.filters import Filter, MetadataFilter
from fastrag.events import Event
from fastrag.plugins import inject
from fastrag.tasks.base import Run, Task


def inject_embedder(**kwargs) -> Embeddings:
    return inject(Embeddings, "OpenAI-Simple", **kwargs)


@dataclass
class OpenAISimple(Task):
    supported: ClassVar[list[str]] = ["OpenAI-Simple", "openai-simple"]
    filter: ClassVar[Filter] = MetadataFilter(step="chunking")

    api_key: InitVar[str]
    url: InitVar[str]
    batch_size: InitVar[int] = 1

    model: str = ""
    embedder: Embeddings | None = None

    def __post_init__(self, api_key: str, url: str, batch_size: int):
        self.embedder = inject_embedder(
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
            metadata={"step": "embedding", "experiment": self.experiment.hash},
        )

        data = json.loads(await cached.get_content())
        if existed and data:
            vectors = []
            documents = []
            for chunk in data:
                vectors.append(chunk.pop("vector"))
                documents.append(Document(**chunk))

            await self.upload_embeddings(documents, vectors)
            yield Event(
                Event.Type.PROGRESS,
                f"Re-uploaded embeddings to {self.experiment.hash}",
            )

        self.results = data

        status = "Cached" if existed else "Generated"
        yield Event(
            Event.Type.PROGRESS,
            f"{self.__class__.__name__} {self.experiment.hash} {status} embeddings for {uri}",
        )

    @override
    def completed_callback(self) -> Event:
        return Event(Event.Type.COMPLETED, f"Completed {self.__class__.__name__}")

    async def embedding_logic(self, entry: CacheEntry) -> bytes:
        raw_json = entry.path.read_text(encoding="utf-8")
        chunks = json.loads(raw_json)

        if not chunks:
            return json.dumps([]).encode("utf-8")

        documents = [Document(**chunk) for chunk in chunks]
        total_vectors = await self.embedder.aembed_documents(documents)

        await self.upload_embeddings(documents, total_vectors)

        for i, chunk in enumerate(chunks):
            chunk["vector"] = total_vectors[i]

        return json.dumps(chunks).encode("utf-8")

    async def upload_embeddings(
        self,
        documents: list[Document],
        embeddings: list[list[float]],
    ) -> None:
        await self.store.add_documents(
            documents,
            embeddings,
            self.experiment.hash,
        )
