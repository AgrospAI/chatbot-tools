from dataclasses import dataclass
from pathlib import Path
from typing import AsyncGenerator, Iterable, override

import humanize

from fastrag.constants import get_constants
from fastrag.fetchers import FetchingEvent, IFetcher
from fastrag.helpers import PathField


def get_uri(p: Path) -> str:
    return p.resolve().as_uri()


def list_paths(p: Path) -> list[Path]:

    if p.is_file():
        return [p]

    if p.is_dir():
        return [p for p in p.glob("*") if p.is_file()]

    raise FileNotFoundError(p)


@dataclass(frozen=True)
class PathFetcher(IFetcher):
    """Copy the source file tree into the cache"""

    path: PathField = PathField()

    @classmethod
    @override
    def supported(cls) -> Iterable[str]:
        return ["Path"]

    @override
    async def fetch(self) -> AsyncGenerator[FetchingEvent, None]:

        yield FetchingEvent(
            FetchingEvent.Type.PROGRESS,
            f"Copying local files ({humanize.naturalsize(self.path.stat().st_size)})",
        )

        try:
            for p in list_paths(self.path):
                existed, _ = await get_constants().cache.get_or_create(
                    uri=p.resolve().as_uri(),
                    step="fetching",
                    contents=p.read_bytes,
                    metadata=None,
                )
                yield FetchingEvent(
                    FetchingEvent.Type.PROGRESS,
                    (
                        f"Skipping local file {self.path.resolve().as_uri()}"
                        if existed
                        else f"Copied local file {self.path.resolve().as_uri()}"
                    ),
                )

        except Exception as e:
            yield FetchingEvent(FetchingEvent.Type.EXCEPTION, f"ERROR: {e}")

        yield FetchingEvent(FetchingEvent.Type.COMPLETED, "Completed local path copy")
