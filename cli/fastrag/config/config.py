from __future__ import annotations

from pathlib import Path

from fastrag.cache.cache import ICache
from fastrag.config.loaders.loader import IConfigLoader
from fastrag.config.models import Config
from fastrag.config.settings import get_settings
from fastrag.embeddings import IEmbeddings
from fastrag.helpers.resources import RuntimeResources
from fastrag.llms.llm import ILLM
from fastrag.plugins import inject
from fastrag.stores.store import IVectorStore


def get_config(path: Path | None = None) -> Config:
    if not path:
        path = get_settings().config_path

    config = inject(IConfigLoader, path.suffix).load(path)
    Config.instance = config

    return config


def get_resources(config: Config) -> RuntimeResources:
    embedding_config = config.experiments.steps["embedding"][0]

    embedding_model = inject(
        IEmbeddings,
        embedding_config.strategy,
        **embedding_config.params,
    )

    cache = inject(
        ICache,
        config.resources.cache.strategy,
        lifespan=config.resources.cache.lifespan,
    )

    store = inject(
        IVectorStore,
        config.resources.store.strategy,
        embedding_model=embedding_model,
        **config.resources.store.params,
    )

    llm = inject(
        ILLM,
        config.resources.llm.strategy,
        **config.resources.llm.params,
    )

    return RuntimeResources(cache=cache, store=store, llm=llm)
