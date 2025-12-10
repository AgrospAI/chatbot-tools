import os
import shutil
import humanize
from dataclasses import dataclass
from typing import AsyncGenerator, Iterable, override

from fastrag.fetchers import Fetcher, FetcherEvent
from fastrag.helpers import PathField, get_constants


@dataclass(frozen=True)
class PathFetcher(Fetcher):
    """Copy the source file tree into the cache"""

    path: PathField = PathField()

    @classmethod
    @override
    def supported(cls) -> Iterable[str]:
        return ["Path"]

    @override
    async def fetch(self) -> AsyncGenerator[FetcherEvent, None]:
        constants = get_constants()
        dest = constants.source / str(hash(self.path))

        yield FetcherEvent(
            FetcherEvent.Type.PROGRESS,
            f"Copying {humanize.naturalsize(self.path.stat().st_size)}",
        )

        try:
            if self.path.is_dir():
                shutil.copytree(self.path, dest, dirs_exist_ok=True)
            elif self.path.is_file():
                os.makedirs(dest, exist_ok=True)
                shutil.copyfile(self.path, dest / self.path.name)
        except Exception as e:
            yield FetcherEvent(FetcherEvent.Type.EXCEPTION, f"ERROR: {e}")
