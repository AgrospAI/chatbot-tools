from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, override

from fastrag.fetchers.fetcher import Fetcher
from fastrag.helpers.url_field import URLField


@dataclass(frozen=True)
class SitemapXMLFetcher(Fetcher):

    url: URLField = URLField()

    @classmethod
    @override
    def supported(cls) -> Iterable[str]:
        return ["SitemapXML"]

    @override
    def fetch(self) -> Iterable[Path]:
        return
