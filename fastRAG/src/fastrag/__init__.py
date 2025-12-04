from pathlib import Path

import fastrag
from fastrag.config import Config, ConfigLoader
from fastrag.plugins import BasePlugin

PACKAGE_DIR = Path(fastrag.__file__).parent.parent.parent
RESOURCES_DIR = PACKAGE_DIR / "resources"
DEFAULT_CONFIG = RESOURCES_DIR / "config.yaml"


__all__ = [BasePlugin, ConfigLoader, Config]
