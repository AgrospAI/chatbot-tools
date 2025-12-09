import os
from pathlib import Path
from typing import Iterable, TextIO, override

import yaml
from dacite import Config as Conf
from dacite import from_dict

from fastrag.config.config import Config
from fastrag.config.loaders.loader import ConfigLoader
from fastrag.helpers.path_field import PathField


class YamlLoader(ConfigLoader):

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return [".yaml", ".yml"]

    @override
    def load(self, fp: TextIO) -> Config:
        data = yaml.safe_load(fp)
        if not data:
            raise ValueError("Config file is empty")

        data = self._expand_env_vars(data)

        return from_dict(
            Config,
            data,
            config=Conf(
                type_hooks={
                    Path: Path,
                }
            ),
        )

    @staticmethod
    def _expand_env_vars(obj):
        if isinstance(obj, dict):
            return {k: YamlLoader._expand_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [YamlLoader._expand_env_vars(v) for v in obj]
        elif isinstance(obj, str):
            # simple ${VAR} replacement
            while "${" in obj and "}" in obj:
                start = obj.find("${")
                end = obj.find("}", start)
                if start == -1 or end == -1:
                    break
                var_name = obj[start + 2 : end]
                var_value = os.environ.get(var_name, "")
                obj = obj[:start] + var_value + obj[end + 1 :]
            return obj
        else:
            return obj
