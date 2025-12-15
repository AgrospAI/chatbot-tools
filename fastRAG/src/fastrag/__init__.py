from pathlib import Path

import fastrag
from fastrag.cache import ICache
from fastrag.config import (
    Benchmarking,
    Cache,
    Chunking,
    Config,
    IConfigLoader,
    Embedding,
    Parsing,
    Source,
    Step,
    Steps,
)
from fastrag.fetchers import IFetcher
from fastrag.helpers import Constants, PathField, URLField, init_constants, version
from fastrag.plugins import BasePlugin, PluginFactory
from fastrag.steps import IStepRunner

PACKAGE_DIR = Path(fastrag.__file__).parent.parent.parent
RESOURCES_DIR = PACKAGE_DIR / "resources"
DEFAULT_CONFIG = RESOURCES_DIR / "config.yaml"


__all__ = [
    BasePlugin,
    PluginFactory,
    IConfigLoader,
    ICache,
    IFetcher,
    Config,
    Source,
    Benchmarking,
    Cache,
    Parsing,
    Chunking,
    Embedding,
    Steps,
    Step,
    PathField,
    URLField,
    init_constants,
    Constants,
    version,
    IStepRunner,
]
