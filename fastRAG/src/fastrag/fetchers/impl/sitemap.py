import asyncio
import io
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncGenerator, Iterable, override
from zipfile import ZipFile

import httpx
from rich.console import Console

from fastrag.fetchers import Fetcher, FetcherEvent
from fastrag.helpers import URLField
from fastrag.helpers.constants import get_constants

console = Console()


@dataclass(frozen=True)
class SitemapXMLFetcher(Fetcher):

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
            data=f"Retrieving {len(urls)} URLs (filtered {skipped}/{len(urls) + skipped})",
        )

        # 3. Fetch filtered URLs
        constants = get_constants()
        dest = constants.source / f"sitemap-{str(hash(self.url))}"
        os.makedirs(dest, exist_ok=True)

        async with httpx.AsyncClient(timeout=10) as client:
            tasks = [self.fetch_async(client, url, dest) for url in urls]
            results = await asyncio.gather(*tasks)

        for event in results:
            if event:
                yield event
        yield FetcherEvent(FetcherEvent.Type.PROGRESS, f"ZIP created: {dest}")

    async def fetch_async(self, client, url: str, dest: Path):
        try:
            res = await client.get(url)
        except Exception as e:
            return FetcherEvent(FetcherEvent.Type.EXCEPTION, f"ERROR: {e}")

        filename = url.replace("https://", "").replace("/", "_") + ".html"
        with open(dest / filename, "w", encoding="utf-8") as f:
            f.write(res.text)

        return FetcherEvent(FetcherEvent.Type.PROGRESS, f"Fetched {filename}")
