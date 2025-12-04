import json
from typing import Iterable, TextIO, override

from fastrag import Config, ConfigLoader


class JsonLoader(ConfigLoader):

    @classmethod
    def supported(cls) -> Iterable[str]:
        return [".json"]

    @override
    def load(self, fp: TextIO) -> Config:
        return Config(**json.loads(fp.read()))
