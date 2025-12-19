from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import AsyncGenerator, ClassVar, override

from html_to_markdown import convert_to_markdown

from fastrag.cache.filters import MetadataFilter, StepFilter
from fastrag.events import Event
from fastrag.helpers.filters import Filter
from fastrag.plugins import plugin
from fastrag.steps.entries import Entries
from fastrag.steps.parsing.events import ParsingEvent
from fastrag.steps.task import Task
from fastrag.systems import System


def read(path: Path) -> bytes:
    md = convert_to_markdown(path.read_text())
    return md.encode()


@dataclass(frozen=True)
@plugin(system=System.PARSING, supported="HtmlParser")
class HtmlParser(Task, Entries):

    filter: ClassVar[Filter] = StepFilter("fetching") & MetadataFilter(format="html")
    use: list[str] = field(default_factory=list, hash=False)

    @override
    async def callback(self) -> AsyncGenerator[ParsingEvent, None]:
        await self.init_entries()
        existed, _ = await self.cache.get_or_create(
            uri=self.entry.path.resolve().as_uri(),
            contents=partial(read, self.entry.path),
            step="parsing",
            metadata={"source": self.uri, "strategy": HtmlParser.supported},
        )
        yield ParsingEvent(
            ParsingEvent.Type.PROGRESS,
            ("Cached" if existed else "Parsing") + f" HTML {self.uri}",
        )

    @override
    def completed_callback(self) -> Event:
        return ParsingEvent(
            ParsingEvent.Type.COMPLETED, f"Parsed {len(self.entries)} HTML documents"
        )
