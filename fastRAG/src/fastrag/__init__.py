from pathlib import Path

import fastrag
from fastrag.cache import ICache
from fastrag.config import (
    Benchmarking,
    Cache,
    Chunking,
    Config,
    Embedding,
    IConfigLoader,
    Parsing,
    Source,
    Step,
    Steps,
)
from fastrag.constants import Constants, get_constants, init_constants
from fastrag.fetchers import IFetcher
from fastrag.helpers import PathField, URLField, version
from fastrag.parsing import IParser
from fastrag.plugins import BasePlugin, IPluginFactory
from fastrag.steps import IStepRunner

PACKAGE_DIR = Path(fastrag.__file__).parent.parent.parent
RESOURCES_DIR = PACKAGE_DIR / "resources"
DEFAULT_CONFIG = RESOURCES_DIR / "config.yaml"


__all__ = [
    BasePlugin,
    IPluginFactory,
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
    get_constants,
    init_constants,
    Constants,
    version,
    IStepRunner,
    IParser,
]
