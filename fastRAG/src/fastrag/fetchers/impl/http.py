from dataclasses import dataclass
from typing import AsyncGenerator, Iterable, override

from httpx import AsyncClient

from fastrag.constants import get_constants
from fastrag.fetchers import FetchingEvent, IFetcher
from fastrag.helpers import URLField


@dataclass(frozen=True)
class HttpFetcher(IFetcher):

    url: URLField = URLField()

    @classmethod
    @override
    def supported(cls) -> Iterable[str]:
        return ["URL"]

    @override
    async def fetch(self) -> AsyncGenerator[FetchingEvent, None]:
        cache = get_constants().cache

        if cache.is_present(self.url):
            yield FetchingEvent(FetchingEvent.Type.COMPLETED, f"Cached {self.url}")
            return

        try:
            async with AsyncClient(timeout=10) as client:
                res = await client.get(self.url)
        except Exception as e:
            yield FetchingEvent(FetchingEvent.Type.EXCEPTION, f"ERROR: {e}")
            return

        yield FetchingEvent(FetchingEvent.Type.COMPLETED, f"Fetched {self.url}")
        await cache.create(
            self.url,
            res.text.encode(),
            "fetching",
            {"format": "html", "strategy": self.supported()[0]},
        )
