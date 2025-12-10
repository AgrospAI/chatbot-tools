import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
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

        async with httpx.AsyncClient(timeout=10) as client:
            with ZipFile(dest, "w") as zpf:
                for url in urls:
                    yield FetcherEvent(FetcherEvent.Type.PROGRESS, f"Fetching {url}")

                    res = await client.get(url)
                    if res.is_error:
                        yield FetcherEvent(
                            FetcherEvent.Type.EXCEPTION, f"Received {res.status_code}"
                        )

                    filename = url.replace("https://", "").replace("/", "_") + ".html"
                    zpf.writestr(filename, res.text)

                    yield FetcherEvent(FetcherEvent.Type.PROGRESS, f"Stored {filename}")

        return
