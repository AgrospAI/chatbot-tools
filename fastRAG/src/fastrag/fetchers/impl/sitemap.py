import asyncio
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import AsyncGenerator, Iterable, override

import httpx

from fastrag.cache.cache import ICache
from fastrag.constants import get_constants
from fastrag.fetchers import FetchingEvent, IFetcher
from fastrag.helpers import URLField


@dataclass(frozen=True)
class SitemapXMLFetcher(IFetcher):

    regex: list[str] | None
    url: URLField = URLField()

    @classmethod
    @override
    def supported(cls) -> Iterable[str]:
        return ["SitemapXML"]

    @override
    async def fetch(self) -> AsyncGenerator[FetchingEvent, None]:
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
            type="progress",
            data=f"Retrieving {len(urls)} URLs (filtered out {skipped} out of {len(urls) + skipped})",
        )

        # 3. Fetch filtered URLs
        cache = get_constants().cache
        async with httpx.AsyncClient(timeout=10) as client:
            tasks = [self.fetch_async(client, url, cache) for url in urls]
            results = await asyncio.gather(*tasks)

        for event in results:
            yield event

        yield FetchingEvent(FetchingEvent.Type.COMPLETED, "Completed sitemap.xml")

    async def fetch_async(self, client, url: str, cache: ICache):
        if cache.is_present(url):
            return FetchingEvent(FetchingEvent.Type.PROGRESS, f"Cached {url}")

        try:
            res = await client.get(url)
        except Exception as e:
            return FetchingEvent(FetchingEvent.Type.EXCEPTION, f"ERROR: {e}")

        await cache.create(
            url,
            res.text.encode(),
            "fetching",
            {"format": "html", "strategy": self.supported()[0]},
        )
        return FetchingEvent(FetchingEvent.Type.PROGRESS, f"Fetching {url}")
