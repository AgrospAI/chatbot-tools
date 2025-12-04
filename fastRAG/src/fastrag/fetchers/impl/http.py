from pathlib import Path
from typing import Iterable, override

from fastrag.fetchers.fetcher import Fetcher


class HttpFetcher(Fetcher):

    @classmethod
    @override
    def fetch(cls, value: str) -> Iterable[Path]: ...
