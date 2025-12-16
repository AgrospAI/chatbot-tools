from dataclasses import dataclass
from typing import AsyncGenerator, Iterable, override

from fastrag.fetchers import FetchingEvent, IFetcher
from fastrag.helpers import URLField


@dataclass(frozen=True)
class HttpFetcher(IFetcher):

    url: URLField = URLField()

    @classmethod
    @override
    def supported(self) -> Iterable[str]:
        return ["URL"]

    @override
    async def fetch(self) -> AsyncGenerator[FetchingEvent, None]:
        yield

        return
