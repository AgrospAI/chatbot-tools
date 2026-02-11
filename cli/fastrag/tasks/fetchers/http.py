from dataclasses import dataclass, field
from typing import ClassVar, override

from httpx import AsyncClient

from fastrag.events import Event
from fastrag.tasks.base import Run, Task


@dataclass
class HttpFetcher(Task):
    supported: ClassVar[str] = "URL"

    url: str
    cached: bool = field(init=False, default=False, hash=False, compare=False)

    @override
    async def run(self) -> Run:
        if self.cache.is_present(self.url):
            self.cached = True
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
            f"{'Cached' if self.cached else 'Fetched'} {self.url}",
        )
