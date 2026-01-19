import json
from dataclasses import InitVar, dataclass, field
from typing import ClassVar, override

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from fastrag.cache.entry import CacheEntry
from fastrag.cache.filters import MetadataFilter
from fastrag.events import Event
from fastrag.helpers.filters import Filter
from fastrag.plugins import inject
from fastrag.steps.task import Run, Task


def inject_embedder(*args, **kwargs) -> Embeddings:
    return inject(Embeddings, "OpenAI-Simple", *args, **kwargs)


@dataclass(frozen=True)
class OpenAISimple(Task):
    supported: ClassVar[list[str]] = ["OpenAI-Simple", "openai-simple"]
    filter: ClassVar[Filter] = MetadataFilter(step="chunking")

    model: str
    api_key: InitVar[str] = field(repr=False)
    url: InitVar[str]
    batch_size: InitVar[int] = 1

    _embedder: Embeddings | None = None

    def __post_init__(self, api_key, url, batch_size):
        embedder = inject_embedder(
            model=self.model,
            api_key=api_key,
            url=url,
            batch_size=batch_size,
        )

        object.__setattr__(self, "_embedder", embedder)

    @override
    async def run(self, uri: str, entry: CacheEntry) -> Run:
        existed, cached = await self.cache.get_or_create(
            uri=f"{entry.path.resolve().as_uri()}.{self.__class__.__name__}.{self.model}.embedding.json",
            contents=lambda: self.embedding_logic(entry),
            metadata={"step": "embedding", "experiment": self.experiment.hash},
        )

        data = json.loads(cached.content)
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

        self.set_results(data)

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
        total_vectors = await self._embedder.aembed_documents(documents)

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
