from abc import ABC, abstractmethod
from typing import Any, List


class Document:
    """Simple document representation"""

    def __init__(self, page_content: str, metadata: dict[str, Any] | None = None):
        self.page_content = page_content
        self.metadata = metadata or {}


class IVectorStore(ABC):
    """Abstract interface for vector store operations"""

    @abstractmethod
    async def add_documents(
        self, documents: List[Document], embeddings: List[List[float]]
    ) -> List[str]:
        """Add documents with their embeddings to the store.

        Args:
            documents: List of documents to store
            embeddings: Corresponding embeddings for each document

        Returns:
            List of document IDs
        """
        pass

    @abstractmethod
    async def similarity_search(
        self, query: str, query_embedding: List[float], k: int = 5
    ) -> List[Document]:
        """Search for similar documents.

        Args:
            query: The query text (for logging/reference)
            query_embedding: The embedding vector of the query
            k: Number of results to return

        Returns:
            List of similar documents
        """
        pass

    @abstractmethod
    async def delete_collection(self) -> None:
        """Delete the entire collection"""
        pass

    @abstractmethod
    async def collection_exists(self) -> bool:
        """Check if the collection exists"""
        pass
