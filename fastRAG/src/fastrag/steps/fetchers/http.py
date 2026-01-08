from dataclasses import dataclass, field
from typing import AsyncGenerator, override

from httpx import AsyncClient

from fastrag.events import Event
from fastrag.helpers import URLField
from fastrag.plugins import plugin
from fastrag.steps.fetchers.events import FetchingEvent
from fastrag.steps.task import Task
from fastrag.systems import System


@dataclass(frozen=True)
@plugin(system=System.FETCHING, supported="URL")
class HttpFetcher(Task):
    url: URLField = URLField()
    _cached: bool = field(init=False, default=False, hash=False, compare=False)

    @override
    async def callback(self) -> AsyncGenerator[Event, None]:
        if self.cache.is_present(self.url):
            object.__setattr__(self, "_cached", True)
            return

        try:
            async with AsyncClient(timeout=10) as client:
                res = await client.get(self.url)
        except Exception as e:
            yield FetchingEvent(FetchingEvent.Type.EXCEPTION, f"ERROR: {e}")
            return

        await self.cache.create(
            self.url,
            res.text.encode(),
            "fetching",
            {"format": "html", "strategy": HttpFetcher.supported},
        )

    @override
    def completed_callback(self) -> Event:
        return FetchingEvent(
            FetchingEvent.Type.COMPLETED,
            f"{'Cached' if self._cached else 'Fetched'} {self.url}",
        )
