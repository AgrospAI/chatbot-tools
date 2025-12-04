from pathlib import Path
from typing import Iterable, override

from fastrag.fetchers.fetcher import Fetcher


class DirectoryFetcher(Fetcher):

    @classmethod
    @override
    def supported(cls) -> Iterable[str]:
        return ["path"]

    @classmethod
    @override
    def fetch(cls, value: str) -> Iterable[Path]: ...
