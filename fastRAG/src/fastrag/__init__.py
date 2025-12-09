from pathlib import Path

import fastrag
from fastrag.config import Config, ConfigLoader, Step, Steps
from fastrag.fetchers import Fetcher
from fastrag.helpers import PathField, URLField
from fastrag.plugins import BasePlugin, PluginFactory

PACKAGE_DIR = Path(fastrag.__file__).parent.parent.parent
RESOURCES_DIR = PACKAGE_DIR / "resources"
DEFAULT_CONFIG = RESOURCES_DIR / "config.yaml"


__all__ = [
    BasePlugin,
    PluginFactory,
    ConfigLoader,
    Fetcher,
    Config,
    Steps,
    Step,
    PathField,
    URLField,
]
