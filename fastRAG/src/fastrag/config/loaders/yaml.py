import os
from pathlib import Path

import yaml
from dacite import Config as Conf
from dacite import from_dict

from fastrag.config.config import Config
from fastrag.plugins.base import plugin


@plugin(key="config", supported=[".yaml", ".yml"])
class YamlLoader:

    def load(self, config: Path) -> Config:
        data = yaml.safe_load(config.read_text())
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
