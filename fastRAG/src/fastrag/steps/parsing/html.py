from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import AsyncGenerator, ClassVar, override
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from html_to_markdown import convert_to_markdown

from fastrag.cache.entry import CacheEntry
from fastrag.cache.filters import MetadataFilter, StepFilter
from fastrag.events import Event
from fastrag.helpers.filters import Filter
from fastrag.plugins import plugin
from fastrag.steps.parsing.events import ParsingEvent
from fastrag.steps.task import Task
from fastrag.systems import System


def read(path: Path, base_url: str) -> bytes:
    html = path.read_text()
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(["a", "img"]):
        attr = "href" if tag.name == "a" else "src"
        if attr in tag.attrs:
            tag[attr] = urljoin(base_url, tag[attr])

    md = convert_to_markdown(str(soup))
    return md.encode()


@dataclass(frozen=True)
@plugin(system=System.PARSING, supported="HtmlParser")
class HtmlParser(Task):

    filter: ClassVar[Filter] = StepFilter("fetching") & MetadataFilter(format="html")
    use: list[str] = field(default_factory=list, hash=False)

    @override
    async def callback(
        self,
        uri: str,
        entry: CacheEntry,
    ) -> AsyncGenerator[ParsingEvent, None]:
        existed, _ = await self.cache.get_or_create(
            uri=entry.path.resolve().as_uri(),
            contents=partial(read, entry.path, entry.metadata["source"]),
            step="parsing",
            metadata={"source": uri, "strategy": HtmlParser.supported},
        )
        yield ParsingEvent(
            ParsingEvent.Type.PROGRESS,
            ("Cached" if existed else "Parsing") + f" HTML {uri}",
        )

    @override
    def completed_callback(self) -> Event:
        return ParsingEvent(
            ParsingEvent.Type.COMPLETED,
            f"Parsed {len(HtmlParser.entries)} HTML documents with HtmlParser",
        )
