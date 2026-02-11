from dataclasses import dataclass
from pathlib import Path

from fastrag.config.models import Config
from fastrag.helpers.resources import RuntimeResources


@dataclass
class AppContext:
    config: Config
    config_path: Path
    plugins_path: Path | None = None
    verbose: bool = False
    resources: RuntimeResources | None = None
