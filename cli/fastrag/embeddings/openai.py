import threading
from dataclasses import dataclass, field
from typing import ClassVar, override

import httpx
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from fastrag.plugins import PluginBase


@dataclass(frozen=True)
class OpenAIEmbeddings(Embeddings, PluginBase):
    """Self-hosted OpenAI-compatible embedding model (synchronous)"""

    supported: ClassVar[list[str]] = ["OpenAI-Simple", "openai-simple"]

    # Shared across all instances to maintain a connection pool
    _client: ClassVar[httpx.Client | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    url: str
    api_key: str = field(repr=False)
    model: str
    batch_size: int = 32
    max_attempts: int = 3

    def get_client(self, api_key: str) -> httpx.Client:
        if OpenAIEmbeddings._client is None or OpenAIEmbeddings._client.is_closed:
            with OpenAIEmbeddings._lock:
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
                    OpenAIEmbeddings._client = httpx.Client(
                        timeout=180.0,
                        headers=headers,
                        limits=limits,
                    )
        return OpenAIEmbeddings._client

    def _embed(self, input_text: str | list[str]) -> list[list[float]] | list[float]:
        """Internal helper to handle the HTTP request logic (sync)."""

        if isinstance(input_text, str):
            batch_input = [input_text]
            single = True
        elif isinstance(input_text, list) and all(isinstance(x, str) for x in input_text):
            batch_input = input_text
            single = False
        else:
            raise TypeError("input_text must be str or list[str]")

        payload = {
            "model": self.model,
            "input": batch_input,
        }

        client = self.get_client(self.api_key)

        response = client.post(self.url, json=payload)
        response.raise_for_status()

        data = response.json()["embeddings"]

        return data[0] if single else data

    @override
    def embed_documents(self, documents: list[str] | list[Document]) -> list[list[float]]:
        if not documents:
            return []

        texts: list[str] = []
        for doc in documents:
            texts.append(doc.page_content if isinstance(doc, Document) else doc)

        all_embeddings: list[list[float]] = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]

            for attempt in range(self.max_attempts):
                try:
                    batch_results = self._embed(batch)
                    break
                except Exception as e:
                    if attempt < self.max_attempts - 1:
                        wait_time = (attempt + 1) * 2
                        print(f"\tERROR in batch {i}, retrying in {wait_time}s... ({e})")
                        import time

                        time.sleep(wait_time)
                    else:
                        raise

            all_embeddings.extend(batch_results)

        return all_embeddings

    @override
    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)
