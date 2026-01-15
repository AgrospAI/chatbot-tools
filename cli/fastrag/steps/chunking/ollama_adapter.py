from typing import List

import httpx
from langchain_core.embeddings import Embeddings


class OpenWebUIEmbeddings(Embeddings):
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        vectors = []
        batch_size = 5

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        with httpx.Client(timeout=120.0) as client:
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i : i + batch_size]

                payload = {
                    "model": self.model,
                    "input": batch_texts,
                }

                response = client.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()

                vectors.extend(result.get("embeddings", []))

        return vectors

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        return self.embed_documents([text])[0]
