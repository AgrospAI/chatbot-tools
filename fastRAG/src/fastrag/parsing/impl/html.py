from dataclasses import dataclass
from typing import AsyncGenerator, Iterable, override

from html_to_markdown import convert_to_markdown

from fastrag.cache.filters import MetadataFilter, StepFilter
from fastrag.constants import get_constants
from fastrag.parsing.parser import IParser, ParsingEvent


@dataclass(frozen=True)
class HtmlParser(IParser):

    use: list[str]

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["HtmlParser"]

    @override
    async def parse(self) -> AsyncGenerator[ParsingEvent, None]:
        cache = get_constants().cache
        filters = StepFilter("fetching") | MetadataFilter(format="html")
        entries = await cache.get_entries(filters)
        total = 0
        for entry in entries:
            md = convert_to_markdown(entry.path.read_text())
            await cache.create(
                entry.path.resolve().as_uri(), md.encode(), "parsing", {}
            )
            total += 1

        yield ParsingEvent(
            ParsingEvent.Type.COMPLETED, f"Parsed {total} HTML documents"
        )
