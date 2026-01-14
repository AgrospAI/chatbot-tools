import asyncio
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import ClassVar, override

import httpx

from fastrag.events import Event
from fastrag.helpers import URLField
from fastrag.steps.task import Run, Task


@dataclass(frozen=True)
class SitemapXMLFetcher(Task):
    supported: ClassVar[str] = "SitemapXML"

    regex: list[str] | None = field(compare=False, hash=False)
    url: URLField = URLField()

    @override
    async def run(self) -> Run:
        # 1. Fetch sitemap
        res = httpx.get(self.url)
        res.raise_for_status()

        # 2. Parse XML
        root = ET.fromstring(res.text)
        urls: list[str] = []
        skipped = 0
        for entry in root.findall("{*}url"):
            loc = entry.find("{*}loc")
            if loc is not None and any(re.search(reg, loc.text) for reg in self.regex):
                urls += [loc.text]
            else:
                skipped += 1

        yield Event(
            type=Event.Type.PROGRESS,
            data=(
                f"Retrieving {len(urls)} URLs "
                f"(filtered out {skipped} out of {len(urls) + skipped})"
            ),
        )

        # 3. Fetch filtered URLs
        async with httpx.AsyncClient(timeout=10) as client:
            tasks = [self.fetch_async(client, url) for url in urls]
            results = await asyncio.gather(*tasks)

        self._set_results([])
        for entry, event in results:
            self.results.append(entry)
            yield event

    async def fetch_async(self, client, url: str):
        if self.cache.is_present(url):
            entry = await self.cache.get(url)
            return entry, Event(Event.Type.PROGRESS, f"Cached {url}")

        try:
            res = await client.get(url)
        except Exception as e:
            return None, Event(Event.Type.EXCEPTION, f"ERROR: {e}")

        entry = await self.cache.create(
            url,
            res.text.encode(),
            {
                "step": "fetching",
                "format": "html",
                "strategy": SitemapXMLFetcher.supported,
            },
        )
        return entry, Event(Event.Type.PROGRESS, f"Fetching {url}")

    @override
    def completed_callback(self) -> Event:
        return Event(Event.Type.COMPLETED, "Completed sitemap.xml")
