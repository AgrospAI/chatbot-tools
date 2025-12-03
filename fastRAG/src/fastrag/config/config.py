from __future__ import annotations

from pathlib import Path
from typing import Iterable, Literal

import yaml

from fastrag.config.loaders.impl.yaml import YamlLoader

EXT = Literal["yaml", "yml"]


class Config:

    supported_extensions: Iterable[EXT] = ["yaml", "yml"]

    @classmethod
    def from_settings(cls, path: Path) -> Config:
        name = path.name.split(".")

        if len(name) == 1:
            raise ValueError("Could not detect extension from config path.")

        extension = name[-1]
        match extension:
            case "yaml" | "yml":
                loader = YamlLoader()
            case _:
                raise ValueError(
                    f"Extension not supported {extension}, supporting: {cls.supported_extensions}"
                )

        with open(path, "rb") as f:
            return loader(f)


del EXT
