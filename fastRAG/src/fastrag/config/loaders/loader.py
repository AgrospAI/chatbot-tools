from __future__ import annotations

from abc import abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, TextIO

from fastrag.config.config import Config
from fastrag.plugins import BasePlugin, PluginRegistry, plugin_registry


class ConfigLoader(BasePlugin):

    registry: PluginRegistry = plugin_registry

    @classmethod
    @abstractmethod
    def extensions(cls) -> Iterable[str]: ...

    @abstractmethod
    def load(self, fp: TextIO) -> Config: ...

    @classmethod
    def get_supported_extensions(cls) -> Dict[str, List[ConfigLoader]]:
        ext_map = defaultdict(list)
        for impl in cls.registry.get(ConfigLoader):
            for ext in impl.extensions():
                ext_map[ext].append(impl)
        return dict(ext_map)

    @classmethod
    def get_supported_loader(cls, ext: str) -> ConfigLoader | None:
        supported = cls.get_supported_extensions()
        loaders = supported.get(ext)
        return loaders[0] if loaders else None

    @classmethod
    def from_settings(cls, settings: Path) -> Config:
        if not settings.exists():
            raise ValueError(f"Could not find config file at {settings.absolute()}")

        ext = settings.suffix
        loader = cls.get_supported_loader(ext)
        if not loader:
            raise ValueError(
                f"Could not find a loader for the settings extension {ext}"
            )

        with open(settings, "r") as f:
            return loader.load(loader, f)
