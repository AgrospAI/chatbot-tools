from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import AsyncGenerator, ClassVar, override

from fastrag.cache.entry import CacheEntry
from fastrag.cache.filters import MetadataFilter, StepFilter
from fastrag.events import Event
from fastrag.helpers.filters import Filter
from fastrag.plugins import plugin
from fastrag.steps.parsing.events import ParsingEvent
from fastrag.steps.task import Task
from fastrag.systems import System


def to_markdown(fmt: str, path: Path) -> bytes:
    match fmt:
        case "pdf":
            from pymupdf4llm import to_markdown

            return to_markdown(path).encode()
        case "docx":
            import pypandoc

            return pypandoc.convert_file(path, "md").encode()
        case _:
            raise TypeError(f"Unsupported file format type: {type(fmt)}")


@dataclass(frozen=True)
@plugin(system=System.PARSING, supported="FileParser")
class FileParser(Task):
    filter: ClassVar[Filter] = StepFilter("fetching") & (
        MetadataFilter(format="docx") | MetadataFilter(format="pdf")
    )
    use: list[str] = field(default_factory=list, hash=False)

    _parsed: int = field(default=0)

    @override
    async def callback(
        self,
        uri: str,
        entry: CacheEntry,
    ) -> AsyncGenerator[Event, None]:
        fmt: str = entry.metadata["format"]
        contents = partial(to_markdown, fmt, entry.path)
        existed, _ = await self.cache.get_or_create(
            uri=entry.path.resolve().absolute().as_uri(),
            contents=contents,
            step="parsing",
            metadata={"source": uri, "strategy": FileParser.supported},
        )
        object.__setattr__(self, "_parsed", self._parsed + 1)
        yield ParsingEvent(
            ParsingEvent.Type.PROGRESS,
            ("Cached" if existed else "Parsing") + f" {fmt.upper()} {uri}",
        )

    @override
    def completed_callback(self) -> Event:
        return ParsingEvent(
            ParsingEvent.Type.COMPLETED,
            f"Parsed {self._parsed} document(s) with FileParser",
        )
