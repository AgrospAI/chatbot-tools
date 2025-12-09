from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, override

from fastrag.fetchers import Fetcher
from fastrag.helpers import URLField


@dataclass(frozen=True)
class HttpFetcher(Fetcher):

    url: URLField = URLField()

    @classmethod
    @override
    def supported(self) -> Iterable[str]:
        return ["URL"]

    @override
    def fetch(self) -> Iterable[Path]:
        return []
