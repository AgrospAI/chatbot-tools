from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import ClassVar, override

from fastrag.cache.entry import CacheEntry
from fastrag.cache.filters import Filter, MetadataFilter
from fastrag.events import Event
from fastrag.tasks.base import Run, Task


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


@dataclass
class FileParser(Task):
    supported: ClassVar[str] = "FileParser"
    filter: ClassVar[Filter] = MetadataFilter(format="docx") | MetadataFilter(format="pdf")

    use: list[str] = field(default_factory=list, hash=False)
    parsed: int = field(default=0, repr=False)

    @override
    async def run(self, uri: str, entry: CacheEntry) -> Run:
        fmt: str = entry.metadata["format"]
        contents = partial(to_markdown, fmt, entry.path)
        existed, entry = await self.cache.get_or_create(
            uri=entry.path.resolve().absolute().as_uri(),
            contents=contents,
            metadata={
                "source": uri,
                "strategy": FileParser.supported,
                "step": "parsing",
            },
        )

        self.parsed += 1

        yield Event(
            Event.Type.PROGRESS,
            ("Cached" if existed else "Parsing")
            + f" {fmt.upper()} {entry.path.resolve().absolute().as_uri()}",
        )

    @override
    def completed_callback(self) -> Event:
        return Event(
            Event.Type.COMPLETED,
            f"Parsed {self.parsed} document(s) with FileParser",
        )
