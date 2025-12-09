from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from fastrag.plugins.base import PluginFactory


class Fetcher(PluginFactory, ABC):

    def __init__(self, *args, **kwargs) -> None: ...

    @abstractmethod
    def fetch(self) -> Iterable[Path]: ...
