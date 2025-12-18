from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import AsyncGenerator, ClassVar, override

from fastrag.cache.filters import MetadataFilter, StepFilter
from fastrag.constants import get_constants
from fastrag.helpers.filters import OrFilter
from fastrag.plugins import plugin
from fastrag.steps.parsing.events import ParsingEvent
from fastrag.steps.parsing.parsing import IParser
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
class FileParser(IParser):

    use: list[str]

    supported_extensions: ClassVar[list[str]] = ["docx", "pdf"]

    @override
    async def parse(self) -> AsyncGenerator[ParsingEvent, None]:
        cache = get_constants().cache
        filters = StepFilter("fetching") | OrFilter(
            *(MetadataFilter(format=f) for f in self.supported_extensions)
        )
        total = 0
        for uri, entry in await cache.get_entries(filters):
            fmt: str = entry.metadata["format"]
            contents = partial(to_markdown, fmt, entry.path)
            existed, entry = await cache.get_or_create(
                uri=entry.path.resolve().absolute().as_uri(),
                contents=contents,
                step="parsing",
                metadata={"source": uri, "strategy": FileParser.supported},
            )
            yield ParsingEvent(
                ParsingEvent.Type.PROGRESS,
                ("Cached" if existed else "Parsing") + f" {fmt.upper()} {uri}",
            )

            total += 1

        yield ParsingEvent(
            ParsingEvent.Type.COMPLETED, f"Parsed {total} File documents"
        )
