from pathlib import Path

import fastrag
from fastrag.config import Config, ConfigLoader, Steps, Step
from fastrag.plugins import BasePlugin, PluginFactory

PACKAGE_DIR = Path(fastrag.__file__).parent.parent.parent
RESOURCES_DIR = PACKAGE_DIR / "resources"
DEFAULT_CONFIG = RESOURCES_DIR / "config.yaml"


__all__ = [BasePlugin, PluginFactory, ConfigLoader, Config, Steps, Step]
