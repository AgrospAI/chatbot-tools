from dataclasses import dataclass

from fastrag.cache.cache import ICache
from fastrag.llms.llm import ILLM
from fastrag.stores.store import IVectorStore


@dataclass(frozen=True)
class RuntimeResources:
    cache: ICache
    store: IVectorStore
    llm: ILLM
