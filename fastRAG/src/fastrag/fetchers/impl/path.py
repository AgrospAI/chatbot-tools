import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, override

from fastrag.fetchers import Fetcher
from fastrag.helpers import PathField, get_constants


@dataclass(frozen=True)
class PathFetcher(Fetcher):
    """Copy the source file tree into the cache"""

    path: PathField = PathField()

    @classmethod
    @override
    def supported(cls) -> Iterable[str]:
        return ["Path"]

    @override
    def fetch(self) -> Iterable[Path]:
        constants = get_constants()
        dest = constants.source / str(hash(self.path))

        if self.path.is_dir():
            shutil.copytree(self.path, dest, dirs_exist_ok=True)
        elif self.path.is_file():
            os.makedirs(dest, exist_ok=True)
            shutil.copyfile(self.path, dest / self.path.name)

        return [dest]
