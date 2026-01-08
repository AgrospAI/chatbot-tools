from abc import ABC, abstractmethod
from typing import List

import requests

from fastrag.plugins import plugin
from fastrag.systems import System


class IEmbeddings(ABC):
    """Abstract interface for embedding models"""

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of documents."""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Embeds a single query."""
        pass


@plugin(system=System.EMBEDDING, supported=["OpenAI-Simple", "openai", "openai-simple"])
class SelfHostedEmbeddings(IEmbeddings):
    """Self-hosted OpenAI-compatible embedding model"""

    def __init__(self, url: str, api_key: str, model: str):
        self.api_url = url
        self.api_key = api_key
        self.model = model

    def _embed(self, input_text: str) -> List[float]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {"model": self.model, "input": input_text}
        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of documents."""
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        """Embeds a single query."""
        return self._embed(text)
