import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

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
