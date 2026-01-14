from dataclasses import dataclass, field
from typing import ClassVar, override

from langchain_core.documents import Document

from fastrag.embeddings.base import IEmbeddings


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
