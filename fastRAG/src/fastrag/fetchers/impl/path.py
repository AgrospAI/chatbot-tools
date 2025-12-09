from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, override

from fastrag.fetchers import Fetcher
from fastrag.helpers import PathField


@dataclass(frozen=True)
class PathFetcher(Fetcher):

    path: PathField = PathField()

    @classmethod
    @override
    def supported(cls) -> Iterable[str]:
        return ["Path"]

    @override
    def fetch(self) -> Iterable[Path]:
        print(self.cache)

        return []
