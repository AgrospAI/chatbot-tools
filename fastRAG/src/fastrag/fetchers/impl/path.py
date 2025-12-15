from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import AsyncGenerator, Iterable, override

import humanize

from fastrag.fetchers import FetcherEvent, IFetcher
from fastrag.helpers import PathField, get_constants


def get_uri(p: Path) -> str:
    return p.resolve().as_uri()


@dataclass(frozen=True)
class PathFetcher(IFetcher):
    """Copy the source file tree into the cache"""

    path: PathField = PathField()

    @classmethod
    @override
    def supported(cls) -> Iterable[str]:
        return ["Path"]

    @override
    async def fetch(self) -> AsyncGenerator[FetcherEvent, None]:

        yield FetcherEvent(
            FetcherEvent.Type.PROGRESS,
            f"Copying local files ({humanize.naturalsize(self.path.stat().st_size)})",
        )

        cache = get_constants().cache
        store = partial(cache.store, section="sourcing")
        path: Path = self.path

        try:
            if path.is_dir():
                for p in path.rglob("*"):
                    if p.is_file():
                        await store(uri=get_uri(p), contents=p.read_bytes())
            elif path.is_file():
                await store(uri=get_uri(path), contents=path.read_bytes())
        except Exception as e:
            yield FetcherEvent(FetcherEvent.Type.EXCEPTION, f"ERROR: {e}")

        yield FetcherEvent(FetcherEvent.Type.PROGRESS, "Completed local path copy")
