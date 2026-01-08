import os
from pathlib import Path

import yaml
from dacite import Config as Conf
from dacite import from_dict

from fastrag.config.config import Config
from fastrag.plugins import plugin
from fastrag.systems import System


def expand_env_vars(obj):
    if isinstance(obj, dict):
        return {k: expand_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [expand_env_vars(v) for v in obj]
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


@plugin(system=System.CONFIG_LOADER, supported=[".yaml", ".yml"])
class YamlLoader:
    def load(self, config: Path) -> Config:
        return from_dict(
            Config,
            expand_env_vars(yaml.safe_load(config.read_text())),
            config=Conf(
                type_hooks={
                    Path: Path,
                }
            ),
        )
