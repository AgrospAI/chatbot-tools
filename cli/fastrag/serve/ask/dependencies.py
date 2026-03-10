from fastapi import Request

from fastrag.embeddings import IEmbeddings
from fastrag.llms import ILLM
from fastrag.stores import IVectorStore


def get_embedding_model(request: Request) -> IEmbeddings:
    return request.app.state.embedding_model


def get_vector_store(request: Request) -> IVectorStore:
    return request.app.state.vector_store


def get_llm(request: Request) -> ILLM:
    return request.app.state.llm
