import os
from pathlib import Path
from typing import Iterable, TextIO, override

import yaml

from fastrag import RESOURCES_DIR
from fastrag.config.config import Config
from fastrag.config.loaders.loader import ConfigLoader


class YamlLoader(ConfigLoader, yaml.SafeLoader):

    @classmethod
    def extensions(cls) -> Iterable[str]:
        return [".yaml", ".yml"]

    @override
    def load(self, fp: TextIO) -> Config:
        data = yaml.safe_load(fp)
        if not data:
            raise ValueError("Config file is empty")

        data = self._expand_env_vars(data)
        data = self._resolve_paths(data)

        try:
            return Config(**data)
        except TypeError as e:
            raise ValueError("Config must be well-formed") from e

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

    @staticmethod
    def _resolve_paths(obj):
        if isinstance(obj, dict):
            return {k: YamlLoader._resolve_paths(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [YamlLoader._resolve_paths(v) for v in obj]
        elif isinstance(obj, str):
            p = Path(obj)
            if not p.is_absolute():
                # treat relative paths as relative to fastrag/resources
                p = (RESOURCES_DIR / p).resolve()
            return p
        else:
            return obj
