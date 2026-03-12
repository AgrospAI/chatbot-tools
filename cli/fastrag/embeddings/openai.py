import asyncio
from dataclasses import dataclass, field
from typing import ClassVar, Sequence, override

import httpx

from fastrag.embeddings import IEmbeddings


def _run(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        return loop.run_until_complete(coro)


@dataclass(frozen=True)
class OpenAIEmbeddings(IEmbeddings):
    """Self-hosted OpenAI-compatible embedding model (synchronous)"""

    supported: ClassVar[list[str]] = ["OpenAI-Simple", "openai-simple"]

    # Shared across all instances to maintain a connection pool
    _client: ClassVar[httpx.AsyncClient | None] = None
    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    url: str
    api_key: str = field(repr=False)
    model: str
    batch_size: int = 4
    max_attempts: int = 3

    async def get_client(self, api_key: str) -> httpx.AsyncClient:
        if OpenAIEmbeddings._client is None or OpenAIEmbeddings._client.is_closed:
            async with OpenAIEmbeddings._lock:
                # Double-check pattern for thread safety
                if OpenAIEmbeddings._client is None or OpenAIEmbeddings._client.is_closed:
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}",
                    }
                    limits = httpx.Limits(
                        max_keepalive_connections=5,
                        max_connections=10,
                    )
                    OpenAIEmbeddings._client = httpx.AsyncClient(
                        timeout=180.0,
                        headers=headers,
                        limits=limits,
                    )
        return OpenAIEmbeddings._client

    async def aquery(self, payload: dict) -> list[list[float]]:
        client = await self.get_client(self.api_key)

        data = {
            "model": self.model,
            **payload,
        }

        response = await client.post(self.url, json=data)

        try:
            response.raise_for_status()
        except Exception as e:
            print("ERROR:", response.text)
            raise e

        return response.json()["embeddings"]

    async def embed(self, input_text: Sequence[str]) -> list[list[float]]:
        return await self.aquery({"input": input_text})

    async def aembed_single(self, input_text: str) -> list[float]:
        result = await self.aquery({"input": [input_text]})
        return result[0]

    @override
    async def get_dimension(self) -> int:
        embedding = await self.aembed_single("test")
        return len(embedding)

    @override
    def embed_documents(self, documents: Sequence[str]) -> list[list[float]]:
        return _run(self.aembed_documents(documents))

    @override
    def embed_query(self, text: str) -> list[float]:
        return _run(self.aembed_query(text))

    @override
    async def aembed_documents(self, documents: Sequence[str]) -> list[list[float]]:
        if not documents:
            return []

        all_embeddings: list[list[float]] = []

        for i in range(0, len(documents), self.batch_size):
            batch = documents[i : i + self.batch_size]

            for attempt in range(self.max_attempts):
                try:
                    batch_results: list[list[int | float]] = await self.embed(batch)
                    break

                except Exception as e:
                    if attempt < self.max_attempts - 1:
                        wait_time = (attempt + 1) * 2
                        print(f"\tERROR in batch {i}, retrying in {wait_time}s... ({e})")
                        await asyncio.sleep(wait_time)
                    elif len(batch) > 1:
                        # Batch failed after all retries — fall back to one-by-one
                        print(f"\tBatch {i} failed, falling back to single embedding...")
                        batch_results = []
                        for doc in batch:
                            # Truncate if too long
                            truncated = doc[:8000]
                            batch_results.append(await self.aembed_single(truncated))
                        break
                    else:
                        raise

            all_embeddings.extend(batch_results)

        return all_embeddings

    @override
    async def aembed_query(self, query: str) -> list[float]:
        return await self.aembed_single(query)
