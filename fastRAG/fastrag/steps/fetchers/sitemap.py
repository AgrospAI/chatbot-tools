import asyncio
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import AsyncGenerator, override

import httpx

from fastrag.events import Event
from fastrag.helpers import URLField
from fastrag.plugins import plugin
from fastrag.steps.fetchers.events import FetchingEvent
from fastrag.steps.task import Task
from fastrag.systems import System


@dataclass(frozen=True)
@plugin(system=System.FETCHING, supported="SitemapXML")
class SitemapXMLFetcher(Task):
    regex: list[str] | None = field(compare=False, hash=False)
    url: URLField = URLField()

    @override
    async def callback(self) -> AsyncGenerator[Event, None]:
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

        yield FetchingEvent(
            type=FetchingEvent.Type.PROGRESS,
            data=(
                f"Retrieving {len(urls)} URLs "
                f"(filtered out {skipped} out of {len(urls) + skipped})"
            ),
        )

        # 3. Fetch filtered URLs
        async with httpx.AsyncClient(timeout=10) as client:
            tasks = [self.fetch_async(client, url) for url in urls]
            results = await asyncio.gather(*tasks)

        for event in results:
            yield event

    async def fetch_async(self, client, url: str):
        if self.cache.is_present(url):
            return FetchingEvent(FetchingEvent.Type.PROGRESS, f"Cached {url}")

        try:
            res = await client.get(url)
        except Exception as e:
            return FetchingEvent(FetchingEvent.Type.EXCEPTION, f"ERROR: {e}")

        await self.cache.create(
            url,
            res.text.encode(),
            "fetching",
            {"format": "html", "strategy": SitemapXMLFetcher.supported},
        )
        return FetchingEvent(FetchingEvent.Type.PROGRESS, f"Fetching {url}")

    @override
    def completed_callback(self) -> Event:
        return FetchingEvent(FetchingEvent.Type.COMPLETED, "Completed sitemap.xml")
