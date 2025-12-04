from typing import Iterable, TextIO

from fastrag import Config, ConfigLoader


class JsonLoader(ConfigLoader):

    @classmethod
    def extensions(cls) -> Iterable[str]:
        return [".json"]

    def load(self, fp: TextIO) -> Config:
        print("Using JsonLoader yay!")

        return Config(test="JSON")
