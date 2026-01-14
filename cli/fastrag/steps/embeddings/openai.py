import asyncio
import json
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
    batch_size: int = field(default=1)
    max_chars_per_request: int = field(default=128)

    _embedded: int = field(default=0, init=False, repr=False)
    _cached: bool = field(default=False, init=False, repr=False)

    @override
    async def run(self, uri: str, entry: CacheEntry) -> Run:
        existed, cached = await self.cache.get_or_create(
            uri=f"{entry.path}.embedding.json",
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

        content_chunks = [c["content"] for c in chunks]

        # split large texts if they exceed max_chars_per_request
        small_chunks = []
        for text in content_chunks:
            if len(text) <= self.max_chars_per_request:
                small_chunks.append(text)
            else:
                for i in range(0, len(text), self.max_chars_per_request):
                    small_chunks.append(text[i : i + self.max_chars_per_request])

        # group into batches
        batches = [
            small_chunks[i : i + self.batch_size]
            for i in range(0, len(small_chunks), self.batch_size)
        ]

        async with httpx.AsyncClient(timeout=120.0) as client:
            tasks = [
                self._send_batch(client, batch, headers, i) for i, batch in enumerate(batches)
            ]
            batch_results = await asyncio.gather(*tasks)

        total_vectors = [vec for batch in batch_results for vec in batch]

        # assign vectors back to chunks (truncate if split into smaller sub-chunks)
        idx = 0
        for chunk in chunks:
            if idx >= len(total_vectors):
                break
            chunk["vector"] = total_vectors[idx]
            idx += 1

        object.__setattr__(self, "_embedded", len(chunks))
        return json.dumps(chunks).encode("utf-8")

    async def _send_batch(self, client: httpx.AsyncClient, batch, headers, idx):
        payload = {"model": self.model, "input": batch}
        try:
            response = await client.post(self.url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            vectors = result.get("embeddings", [])
            if len(vectors) != len(batch):
                raise ValueError(
                    f"Batch {idx}: Sent {len(batch)} texts but got {len(vectors)} vectors"
                )
            return vectors
        except httpx.HTTPStatusError as e:
            # log server response for debugging
            try:
                detail = await e.response.aread()
                print(f"Batch {idx} failed: {detail.decode()}")
            except Exception:
                pass
            raise RuntimeError(f"Embedding failed at batch {idx}: {e}")
        except Exception as e:
            raise RuntimeError(f"Embedding failed at batch {idx}: {e}")
