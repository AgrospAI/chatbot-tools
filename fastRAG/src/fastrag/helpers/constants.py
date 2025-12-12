import os
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar


@dataclass(frozen=True)
class Constants:
    base: Path

    global_: ClassVar[Path] = Path.home().joinpath(".fastrag")

    @classmethod
    def global_cache(cls) -> Path:
        return cls.global_ / "caches"

    @property
    def source(self) -> Path:
        return self.base / "source"

    def __post_init__(self) -> None:
        # Ensure all paths exist
        os.makedirs(self.global_, exist_ok=True)
        os.makedirs(self.base, exist_ok=True)
        os.makedirs(self.source, exist_ok=True)


# Global singleton
_constants: Constants | None = None


def _register_constants(constants: Constants) -> None:
    # Stores the path of the cache to a global .fastrag file

    with open(Constants.global_cache(), "w+") as f:
        lines = f.readlines()

        if constants.base in lines:
            return

        f.write(str(constants.base.absolute()))


def init_constants(cache: Path) -> None:
    global _constants
    if _constants is None:
        _constants = Constants(cache)
        _register_constants(_constants)


def get_constants() -> Constants:
    if _constants is None:
        raise RuntimeError(
            "Constants not initialized. Call init_constants(config) first."
        )
    return _constants
