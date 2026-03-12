from abc import ABC, abstractmethod
from typing import Sequence

from fastrag.plugins import PluginBase


class IEmbeddings(PluginBase, ABC):
    @abstractmethod
    async def get_dimension(self) -> int:
        """Get the embedding dimensions

        Returns:
            int: embedding dimension
        """

    @abstractmethod
    def embed_documents(self, documents: Sequence[str]) -> list[list[float]]:
        """Embed documents

        Args:
            documents: List of text to embed.

        Returns:
            List of embeddings.
        """

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Embed query text.

        Args:
            text: Text to embed.

        Returns:
            Embedding.
        """

    @abstractmethod
    async def aembed_documents(self, documents: Sequence[str]) -> list[list[float]]:
        """Embed the given documents

        Args:
            documents (Sequence[str]): to embed

        Returns:
            Sequence[Sequence[float]]: Sequence of embeddings
        """

    @abstractmethod
    async def aembed_query(self, query: str) -> list[float]:
        """Embed a query

        Args:
            query (str): to embed

        Returns:
            Sequence[float]: Embeddings representing the query
        """
