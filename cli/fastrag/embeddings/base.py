from abc import ABC, abstractmethod

from fastrag.plugins import PluginBase


class IEmbeddings(PluginBase, ABC):
    """Abstract interface for embedding models"""

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embeds a list of documents."""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Embeds a single query."""
        pass
