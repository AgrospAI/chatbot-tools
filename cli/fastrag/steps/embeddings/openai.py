import json
import httpx
from dataclasses import dataclass, field
from functools import partial
from typing import AsyncGenerator, ClassVar, override

from fastrag.cache.entry import CacheEntry
from fastrag.cache.filters import MetadataFilter
from fastrag.events import Event
from fastrag.helpers.filters import Filter
from fastrag.steps.task import Task


@dataclass(frozen=True)
class SelfHostedEmbeddings(Task):
    supported: ClassVar[list[str]] = ["OpenAI-Simple", "openai", "openai-simple"]
    filter: ClassVar[Filter] = MetadataFilter(step="chunking")

    model: str
    api_key: str
    url: str
    batch_size: int = 1

    _embedded: int = field(default=0, init=False)
    _cached: bool = field(default=False, init=False)

    @override
    async def callback(
        self,
        uri: str,
        entry: CacheEntry,
    ) -> AsyncGenerator[Event, None]:
        existed, cached = await self.cache.get_or_create(
            uri=f"{uri}.embedding.json",
            contents=partial(self.embedding_logic, entry),
            metadata={
                "step": "embedding",
                "model": self.model,
                "api": "ollama-openwebui-agrospai",
            },
        )

        if existed:
            data = json.loads(cached.content)
            object.__setattr__(self, "_embedded", len(data))
            object.__setattr__(self, "_cached", True)
        
        status = "Cached" if existed else "Generated"
        yield Event(Event.Type.PROGRESS, f"{status} embeddings for {uri}")

    @override
    def completed_callback(self) -> Event:
        status = f"Embedding done{' (cached)' if self._cached else ''}"
        return Event(Event.Type.COMPLETED, f"{status} {self._embedded} vectors")

    def embedding_logic(self, entry: CacheEntry) -> bytes:
        raw_json = entry.path.read_text(encoding="utf-8")
        chunks = json.loads(raw_json)
        
        if not chunks:
            return json.dumps([]).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        total_vectors = []
        content_chunks = [c["content"] for c in chunks]

        with httpx.Client(timeout=120.0) as client:
            for i in range(0, len(content_chunks), self.batch_size):
                # Send to embedding model by batches size
                batch_texts = content_chunks[i : i + self.batch_size]
                
                payload = {
                    "model": self.model,
                    "input": batch_texts,
                }

                try:
                    response = client.post(self.url, headers=headers, json=payload)
                    response.raise_for_status()
                    
                    result = response.json()
                    batch_vectors = result.get("embeddings", [])
                    
                    if len(batch_vectors) != len(batch_texts):
                        raise ValueError(f"Sent {len(batch_texts)} texts but got {len(batch_vectors)} vectors.")
                        
                    total_vectors.extend(batch_vectors)
                    
                except Exception as e:
                    raise RuntimeError(f"Embedding failed at chunk {i}: {e}")

        for i, chunk in enumerate(chunks):
            chunk["vector"] = total_vectors[i]

        object.__setattr__(self, "_embedded", len(chunks))
        return json.dumps(chunks).encode("utf-8")