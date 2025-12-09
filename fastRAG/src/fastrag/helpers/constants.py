from dataclasses import dataclass
from functools import cached_property
from pathlib import Path


@dataclass(frozen=True)
class Constants:
    base: Path

    @cached_property
    def source(self) -> Path:
        return self.base / "source"


# Global singleton
_constants: Constants | None = None


def init_constants(cache: Path) -> None:
    global _constants
    if _constants is None:
        _constants = Constants(cache)


def get_constants() -> Constants:
    if _constants is None:
        raise RuntimeError(
            "Constants not initialized. Call init_constants(config) first."
        )
    return _constants
