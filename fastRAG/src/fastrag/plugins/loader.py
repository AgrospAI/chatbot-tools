import importlib
import pkgutil
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Iterable

from fastrag.plugins.condition import Condition


@dataclass(frozen=True)
class HasPrefixCondition:

    prefixes: Iterable[str]

    def check(self, name: str) -> bool:
        return name.startswith(self.prefixes)


def load_directory(dir: Path, conditions: Iterable[Condition]) -> dict[str, ModuleType]:
    """Load the plugins from a given directory.

    Args:
        dir (Path): directory to analyze
        conditions (Iterable[Condition]): list of conditions to check the
    Returns:
        dict[str, object]: Names to plugins
    """

    return {
        name: importlib.import_module(name)
        for _, name, _ in pkgutil.iter_modules(dir)
        if any([c(name) for c in conditions])
    }
