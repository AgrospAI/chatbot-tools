import asyncio
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import AsyncGenerator, Iterable, override

import httpx
from rich.console import Console

from fastrag.cache.cache import ICache
from fastrag.constants import get_constants
from fastrag.fetchers import FetcherEvent, IFetcher
from fastrag.helpers import URLField

console = Console()


@dataclass(frozen=True)
class SitemapXMLFetcher(IFetcher):

    regex: list[str] | None
    url: URLField = URLField()

    @classmethod
    @override
    def supported(cls) -> Iterable[str]:
        return ["SitemapXML"]

    @override
    async def fetch(self) -> AsyncGenerator[FetcherEvent, None]:
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

        yield FetcherEvent(
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

        yield FetcherEvent(FetcherEvent.Type.COMPLETED, "Completed sitemap.xml")

    async def fetch_async(self, client, url: str, cache: ICache):
        if cache.is_present(url):
            return FetcherEvent(FetcherEvent.Type.PROGRESS, f"Cached {url}")

        try:
            res = await client.get(url)
        except Exception as e:
            return FetcherEvent(FetcherEvent.Type.EXCEPTION, f"ERROR: {e}")

        await cache.create(url, res.text.encode(), "sourcing", {})
        return FetcherEvent(FetcherEvent.Type.PROGRESS, f"Fetched {url}")
