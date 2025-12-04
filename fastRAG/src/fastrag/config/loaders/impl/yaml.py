from typing import Iterable, TextIO, override

import yaml

from fastrag.config.config import Config
from fastrag.config.loaders.loader import ConfigLoader


class YamlLoader(ConfigLoader, yaml.SafeLoader):

    @classmethod
    def extensions(cls) -> Iterable[str]:
        return [".yaml", ".yml"]

    @override
    def load(self, fp: TextIO) -> Config:
        return Config(**yaml.safe_load(fp))
