from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import AsyncGenerator, override

from html_to_markdown import convert_to_markdown

from fastrag.cache.filters import MetadataFilter, StepFilter
from fastrag.constants import get_constants
from fastrag.parsing.events import ParsingEvent
from fastrag.plugins.base import plugin


def read(path: Path) -> bytes:
    md = convert_to_markdown(path.read_text())
    return md.encode()


@dataclass(frozen=True)
@plugin(key="parsing", supported="HtmlParser")
class HtmlParser:

    use: list[str]

    @override
    async def parse(self) -> AsyncGenerator[ParsingEvent, None]:
        cache = get_constants().cache
        filters = StepFilter("fetching") | MetadataFilter(format="html")
        total = 0
        for uri, entry in await cache.get_entries(filters):
            contents = partial(read, entry.path)
            existed, entry = await cache.get_or_create(
                uri=entry.path.resolve().as_uri(),
                contents=contents,
                step="parsing",
                metadata={"source": uri, "strategy": HtmlParser.supported},
            )
            yield ParsingEvent(
                ParsingEvent.Type.PROGRESS,
                ("Cached" if existed else "Parsing") + f" HTML {uri}",
            )

            total += 1

        yield ParsingEvent(
            ParsingEvent.Type.COMPLETED, f"Parsed {total} HTML documents"
        )
