from dataclasses import dataclass
from typing import Iterable, TextIO, override

from fastrag.config.config import Config
from fastrag.config.loaders.loader import ConfigLoader


@dataclass(frozen=True)
class JsonLoader(ConfigLoader):

    @classmethod
    def extensions(cls) -> Iterable[str]:
        return [".json"]

    @override
    def load(self, fp: TextIO) -> Config:
        print("Running JsonLoader load")
