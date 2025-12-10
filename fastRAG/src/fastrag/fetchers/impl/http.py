from dataclasses import dataclass
from typing import AsyncGenerator, Iterable, override

from fastrag.fetchers import Fetcher, FetcherEvent
from fastrag.helpers import URLField


@dataclass(frozen=True)
class HttpFetcher(Fetcher):

    url: URLField = URLField()

    @classmethod
    @override
    def supported(self) -> Iterable[str]:
        return ["URL"]

    @override
    async def fetch(self) -> AsyncGenerator[FetcherEvent, None]:
        yield

        return
