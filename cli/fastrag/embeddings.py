import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar, override

import httpx
from langchain_core.documents import Document

from fastrag.plugins import PluginBase


@dataclass(frozen=True)
class IEmbeddings(PluginBase, ABC):
    """Abstract interface for embedding models"""

    # Shared across all instances to maintain a connection pool
    _client: ClassVar[httpx.AsyncClient | None] = None
    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    async def get_client(self, api_key: str) -> httpx.AsyncClient:
        if IEmbeddings._client is None or IEmbeddings._client.is_closed:
            async with IEmbeddings._lock:
                # Double-check pattern for thread/async safety
                if IEmbeddings._client is None or IEmbeddings._client.is_closed:
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}",
                    }
                    # We store the client on the base class to ensure it's a true singleton
                    IEmbeddings._client = httpx.AsyncClient(
                        timeout=120.0,
                        headers=headers,
                    )
        return IEmbeddings._client

    @abstractmethod
    async def embed_documents(self, texts: list[Document]) -> list[list[float]]:
        """Embeds a list of documents."""

        raise NotImplementedError

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """Embeds a single query."""

        raise NotImplementedError


@dataclass(frozen=True)
class SelfHostedEmbeddings(IEmbeddings):
    """Self-hosted OpenAI-compatible embedding model"""

    supported: ClassVar[list[str]] = ["OpenAI-Simple", "openai-simple"]

    url: str
    api_key: str = field(repr=False)
    model: str
    batch_size: int = 32

    async def _embed(self, input_text: str | list[str]) -> list[list[float]] | list[float]:
        """Internal helper to handle the HTTP request logic."""
        payload = {"model": self.model, "input": input_text}

        client = await self.get_client(self.api_key)

        response = await client.post(self.url, json=payload)
        response.raise_for_status()

        response = response.json()

        if isinstance(input_text, str):
            return response["embeddings"][0]
        return response["embeddings"]

    @override
    async def embed_documents(self, documents: list[Document]) -> list[list[float]]:
        if not documents:
            return []

        all_embeddings = []

        texts = [doc.page_content for doc in documents]

        # 2. Batch the extracted strings
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            batch_results = await self._embed(batch)
            all_embeddings.extend(batch_results)

        return all_embeddings

    @override
    async def embed_query(self, text: str) -> list[float]:
        return await self._embed(text)
