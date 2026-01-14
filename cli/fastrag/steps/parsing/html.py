from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import ClassVar, override
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from html_to_markdown import convert_to_markdown

from fastrag.cache.entry import CacheEntry
from fastrag.cache.filters import MetadataFilter
from fastrag.events import Event
from fastrag.helpers.filters import Filter
from fastrag.steps.task import Run, Task


def parse_to_md(path: Path, base_url: str) -> bytes:
    html = path.read_text()
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(["a", "img"]):
        attr = "href" if tag.name == "a" else "src"
        if attr in tag.attrs:
            tag[attr] = urljoin(base_url, tag[attr])

    md = convert_to_markdown(str(soup))
    return md.encode()


@dataclass(frozen=True)
class HtmlParser(Task):
    supported: ClassVar[str] = "HtmlParser"
    filter: ClassVar[Filter] = MetadataFilter(step="fetching", format="html")

    use: list[str] = field(default_factory=list, hash=False)
    _parsed: int = field(default=0)

    @override
    async def run(self, uri: str, entry: CacheEntry) -> Run:
        existed, _ = await self.cache.get_or_create(
            uri=entry.path.resolve().as_uri(),
            contents=partial(parse_to_md, entry.path, uri),
            metadata={
                "source": uri,
                "strategy": HtmlParser.supported,
                "step": "parsing",
            },
        )
        object.__setattr__(self, "_parsed", self._parsed + 1)
        yield Event(
            Event.Type.PROGRESS,
            ("Cached" if existed else "Parsing") + f" HTML {uri}",
        )

    @override
    def completed_callback(self) -> Event:
        return Event(
            Event.Type.COMPLETED,
            f"Parsed {self._parsed} HTML documents with HtmlParser",
        )
