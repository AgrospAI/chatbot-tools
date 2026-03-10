from fastrag.embeddings.embeddings import IEmbeddings

from .openai import OpenAIEmbeddings

__all__ = ["OpenAIEmbeddings", "IEmbeddings"]
