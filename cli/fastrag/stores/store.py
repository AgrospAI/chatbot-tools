from abc import ABC, abstractmethod
from typing import Any, List

from fastrag.plugins import PluginBase


class Document:
    """Simple document representation"""

    def __init__(self, page_content: str, metadata: dict[str, Any] | None = None):
        self.page_content = page_content
        self.metadata = metadata or {}


class IVectorStore(PluginBase, ABC):
    """Abstract interface for vector store operations"""

    @abstractmethod
    async def add_documents(
        self,
        documents: List[Document],
        embeddings: List[List[float]],
        collection_name: str | None = None,
    ) -> List[str]:
        """Add documents with their embeddings to the store.

        Args:
            documents: List of documents to store
            embeddings: Corresponding embeddings for each document
            collection_name: Collection to add documents to

        Returns:
            List of document IDs
        """
        pass

    @abstractmethod
    async def similarity_search(
        self,
        query: str,
        query_embedding: List[float],
        k: int = 5,
        collection_name: str | None = None,
    ) -> List[Document]:
        """Search for similar documents.

        Args:
            query: The query text (for logging/reference)
            query_embedding: The embedding vector of the query
            k: Number of results to return
            collection_name: Collection to add documents to

        Returns:
            List of similar documents
        """
        pass

    @abstractmethod
    async def delete_collection(self, collection_name: str | None = None) -> None:
        """Delete the entire collection"""
        pass

    @abstractmethod
    async def collection_exists(self, collection_name: str | None = None) -> bool:
        """Check if the collection exists"""
        pass

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """Embeds a single query."""

        pass
