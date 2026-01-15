import json
import asyncio
from dataclasses import dataclass, field
from functools import partial
from typing import ClassVar, override

import httpx

from fastrag.cache.entry import CacheEntry
from fastrag.cache.filters import MetadataFilter
from fastrag.events import Event
from fastrag.helpers.filters import Filter
from fastrag.steps.task import Run, Task

@dataclass(frozen=True)
class SelfHostedEmbeddings(Task):
    supported: ClassVar[list[str]] = ["OpenAI-Simple", "openai", "openai-simple"]
    filter: ClassVar[Filter] = MetadataFilter(step="chunking")

    model: str
    api_key: str = field(repr=False)
    url: str
    batch_size: int = field(default=5)

    _embedded: int = field(default=0, init=False, repr=False)
    _cached: bool = field(default=False, init=False, repr=False)

    @override
    async def run(self, uri: str, entry: CacheEntry) -> Run:
        existed, cached = await self.cache.get_or_create(
            uri=f"{entry.path.resolve().as_uri()}.embedding.json",
            contents=lambda: self.embedding_logic(entry),
            metadata={
                "step": "embedding",
                "model": self.model,
                "api": "ollama-openwebui-agrospai",
            },
        )

        data = json.loads(cached.content)
        object.__setattr__(self, "_embedded", len(data))
        object.__setattr__(self, "_cached", existed)
        self._set_results(data)

        status = "Cached" if existed else "Generated"
        yield Event(Event.Type.PROGRESS, f"{status} embeddings for {uri}")

    @override
    def completed_callback(self) -> Event:
        status = f"Embedding done{' (cached)' if self._cached else ''}"
        return Event(Event.Type.COMPLETED, f"{status} {self._embedded} vectors")

    async def embedding_logic(self, entry: CacheEntry) -> bytes:
        raw_json = entry.path.read_text(encoding="utf-8")
        chunks = json.loads(raw_json)

        if not chunks:
            return json.dumps([]).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        result_vectors = []
        content_chunks = [c["page_content"] for c in chunks]

        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        
        async with httpx.AsyncClient(timeout=180.0, limits=limits) as client:
            for i in range(0, len(content_chunks), self.batch_size):
                # Send to embedding model by batches size
                batch_texts = content_chunks[i : i + self.batch_size]

                payload = {
                    "model": self.model,
                    "input": batch_texts,
                }

                for attempt in range(3):
                    try:
                        response = await client.post(self.url, headers=headers, json=payload)
                        response.raise_for_status()

                        result = response.json()
                        batch_vectors = result.get("embeddings", [])
                        
                        if len(batch_vectors) != len(batch_texts):
                            raise ValueError(f"Sent {len(batch_texts)} texts, received {len(batch_vectors)} vectors.")

                        if not batch_vectors:
                             raise ValueError(f"Server returned empty list. Response: {result}")

                        result_vectors.extend(batch_vectors)
                        await asyncio.sleep(0.5) 
                        break

                    except Exception as e:
                        if attempt < 2:
                            wait_time = (attempt + 1) * 2
                            print(f"Error in batch {i}, retrying in {wait_time}s... ({e})")
                            await asyncio.sleep(wait_time)
                        else:
                            raise RuntimeError(f"Permanent failure in batch {i}: {e}")

        for i, chunk in enumerate(chunks):
            chunk["vector"] = result_vectors[i]

        object.__setattr__(self, "_embedded", len(result_vectors))
        return json.dumps(chunks).encode("utf-8")
