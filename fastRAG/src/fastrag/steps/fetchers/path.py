from dataclasses import dataclass
from pathlib import Path
from typing import AsyncGenerator, override

import humanize

from fastrag.constants import get_constants
from fastrag.helpers import PathField
from fastrag.plugins import plugin
from fastrag.steps.fetchers.events import FetchingEvent
from fastrag.steps.fetchers.fetcher import IFetcher
from fastrag.systems import System


def get_uri(p: Path) -> str:
    return p.resolve().as_uri()


def list_paths(p: Path) -> list[Path]:
    if p.is_file():
        return [p]
    if p.is_dir():
        return [p for p in p.glob("*") if p.is_file()]

    raise FileNotFoundError(p)


@dataclass(frozen=True)
@plugin(system=System.FETCHING, supported="Path")
class PathFetcher(IFetcher):

    path: PathField = PathField()

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
                    metadata={
                        "format": p.suffix[1:],
                        "strategy": PathFetcher.supported,
                    },
                )
                yield FetchingEvent(
                    FetchingEvent.Type.PROGRESS,
                    (
                        ("Cached" if existed else "Copied")
                        + f" local path {p.resolve().as_uri()}"
                    ),
                )

        except Exception as e:
            yield FetchingEvent(FetchingEvent.Type.EXCEPTION, f"ERROR: {e}")

        yield FetchingEvent(FetchingEvent.Type.COMPLETED, "Completed local path copy")
