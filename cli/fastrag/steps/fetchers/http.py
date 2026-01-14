from dataclasses import dataclass, field
from typing import AsyncGenerator, ClassVar, override

from httpx import AsyncClient

from fastrag.events import Event
from fastrag.helpers import URLField
from fastrag.steps.task import Task


@dataclass(frozen=True)
class HttpFetcher(Task):
    supported: ClassVar[str] = "URL"

    url: URLField = URLField()
    _cached: bool = field(init=False, default=False, hash=False, compare=False)

    @override
    async def run(self) -> AsyncGenerator[Event, None]:
        if self.cache.is_present(self.url):
            object.__setattr__(self, "_cached", True)
            return

        try:
            async with AsyncClient(timeout=10) as client:
                res = await client.get(self.url)
        except Exception as e:
            yield Event(Event.Type.EXCEPTION, f"ERROR: {e}")
            return

        entry = await self.cache.create(
            self.url,
            res.text.encode(),
            {
                "step": "fetching",
                "format": "html",
                "strategy": HttpFetcher.supported,
            },
        )

        self.result = entry.path

    @override
    def completed_callback(self) -> Event:
        return Event(
            Event.Type.COMPLETED,
            f"{'Cached' if self._cached else 'Fetched'} {self.url}",
        )
