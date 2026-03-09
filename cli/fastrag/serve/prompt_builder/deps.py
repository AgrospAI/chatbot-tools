from typing import Annotated

from fastapi import Depends
from langchain_core.embeddings import Embeddings

from fastrag.serve.ask.dependencies import get_embedding_model, get_vector_store
from fastrag.serve.prompt_builder.interfaces import IPromptBuilder
from fastrag.serve.prompt_builder.service import PromptBuilder
from fastrag.stores import IVectorStore


def get_prompt_builder(
    embedding_model: Annotated[Embeddings, Depends(get_embedding_model)],
    vector_store: Annotated[IVectorStore, Depends(get_vector_store)],
) -> IPromptBuilder:
    return PromptBuilder(
        embedding_model=embedding_model,
        vector_store=vector_store,
    )
