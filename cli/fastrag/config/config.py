from __future__ import annotations

from pathlib import Path

from langchain_core.embeddings import Embeddings

from fastrag.cache.cache import ICache
from fastrag.config.loaders.loader import IConfigLoader
from fastrag.config.models import Config
from fastrag.config.settings import settings
from fastrag.helpers.resources import RuntimeResources
from fastrag.llms.llm import ILLM
from fastrag.plugins import inject
from fastrag.stores.store import IVectorStore


def get_config(path: Path = settings.fastrag_config_path) -> Config:
    config = inject(IConfigLoader, path.suffix).load(path)
    Config.instance = config

    return config


def get_resources(config: Config) -> RuntimeResources:
    embedding_config = config.experiments.steps["embedding"][0]
    embedding_model = inject(Embeddings, embedding_config.strategy, **embedding_config.params)

    return RuntimeResources(
        cache=inject(
            ICache,
            config.resources.cache.strategy,
            lifespan=config.resources.cache.lifespan,
        ),
        store=inject(
            IVectorStore,
            config.resources.store.strategy,
            embedding_model=embedding_model,
            **config.resources.store.params,
        ),
        llm=inject(
            ILLM,
            config.resources.llm.strategy,
            **config.resources.llm.params,
        ),
    )
