from typing import Optional

from langchain_core.embeddings import Embeddings

from fastrag import ILLM, Config
from fastrag.stores.store import IVectorStore

# These will be set at app startup
vector_store: Optional[IVectorStore] = None
llm: Optional[ILLM] = None
config: Optional[Config] = None
embedding_model: Optional[Embeddings] = None


def set_dependencies(cfg: Config, vs: IVectorStore, llm_model: ILLM, emb: Embeddings):
    global config, vector_store, llm, embedding_model
    config = cfg
    vector_store = vs
    llm = llm_model
    embedding_model = emb


def get_vector_store():
    return vector_store


def get_llm():
    return llm


def get_config():
    return config


def get_embedding_model():
    return embedding_model
