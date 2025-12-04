from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TextIO

from rich.console import Console

from fastrag.config.config import Config
from fastrag.plugins.base import PluginFactory

console = Console()


class ConfigLoader(PluginFactory, ABC):

    @abstractmethod
    def load(self, fp: TextIO) -> Config: ...

    @classmethod
    def from_settings(cls, settings: Path) -> Config:
        if not settings.exists():
            raise ValueError(f"Could not find config file at {settings.absolute()}")

        ext = settings.suffix
        loader = ConfigLoader.get_supported_instance(ext)
        if not loader:
            raise ValueError(
                f"Could not find a loader for the settings extension {ext}"
            )

        console.print(
            f"Loading config with [bold red]{loader.__name__}[/bold red] class"
        )

        with open(settings, "r") as f:
            return loader.load(loader, f)
