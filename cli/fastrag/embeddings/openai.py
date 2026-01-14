import requests

from fastrag.embeddings.base import IEmbeddings


class OpenAIEmbeddings(IEmbeddings):
    """Self-hosted OpenAI-compatible embedding model"""

    supported: list[str] = ["OpenAIEmbeddings"]

    def __init__(self, url: str, api_key: str, model: str):
        self.api_url = url
        self.api_key = api_key
        self.model = model

    def _embed(self, input_text: str) -> list[float]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {"model": self.model, "input": input_text}
        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embeds a list of documents."""
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        """Embeds a single query."""
        return self._embed(text)
