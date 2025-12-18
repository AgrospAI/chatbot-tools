from dataclasses import dataclass
from typing import AsyncGenerator, override

from httpx import AsyncClient

from fastrag.constants import get_constants
from fastrag.helpers import URLField
from fastrag.plugins import plugin
from fastrag.steps.fetchers.events import FetchingEvent
from fastrag.steps.fetchers.fetcher import IFetcher
from fastrag.systems import System


@dataclass(frozen=True)
@plugin(system=System.FETCHING, supported="URL")
class HttpFetcher(IFetcher):

    url: URLField = URLField()

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
            {"format": "html", "strategy": HttpFetcher.supported},
        )
