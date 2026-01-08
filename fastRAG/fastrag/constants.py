import os
from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import ClassVar

from fastrag import Config, ICache
from fastrag.plugins import PluginRegistry
from fastrag.systems import System


@dataclass(frozen=True)
class Constants:
    config: InitVar[Config]

    verbose: bool = field()
    base: Path = field(init=False)
    cache: ICache = field(init=False)

    global_: ClassVar[Path] = Path.home().joinpath(".fastrag")

    def __post_init__(self, config: Config) -> None:
        for k, v in {
            "base": config.cache.path,
            "cache": PluginRegistry.get_instance(
                System.CACHE,
                "local",
                base=config.cache.path,
                lifespan=config.cache.lifespan,
            ),
        }.items():
            object.__setattr__(self, k, v)

        # Ensure all paths exist
        for path in [self.global_, self.base]:
            os.makedirs(path, exist_ok=True)

    @classmethod
    def global_cache(cls) -> Path:
        return cls.global_ / "caches"


# Global singleton
_constants: Constants | None = None


def _register_constants(constants: Constants) -> None:
    # Stores the path of the cache to a global .fastrag file

    with open(Constants.global_cache(), "w+") as f:
        lines = f.readlines()

        if constants.base in lines:
            return

        f.write(str(constants.base.absolute()))


def init_constants(config: Config, is_verbose: bool) -> None:
    global _constants
    if _constants is None:
        _constants = Constants(config, is_verbose)
        _register_constants(_constants)


def get_constants() -> Constants:
    if _constants is None:
        raise RuntimeError("Constants not initialized. Call init_constants(config) first.")
    return _constants
