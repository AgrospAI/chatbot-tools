from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import ClassVar, override

import humanize

from fastrag.events import Event
from fastrag.tasks.base import Run, Task


def get_uri(p: Path) -> str:
    return p.resolve().as_uri()


def list_paths(p: Path) -> list[Path]:
    if p.is_file():
        return [p]
    if p.is_dir():
        return [p for p in p.glob("*") if p.is_file()]

    raise FileNotFoundError(p)


@dataclass
class PathFetcher(Task):
    supported: ClassVar[str] = "Path"

    path: InitVar[str]

    _path: Path = field(init=False)

    def __post_init__(self, path: str) -> None:
        self._path = Path(path)
        assert self._path.exists()

    @override
    async def run(self) -> Run:
        yield Event(
            Event.Type.PROGRESS,
            f"Copying local files ({humanize.naturalsize(self._path.stat().st_size)})",
        )

        self.results = []
        try:
            for p in list_paths(self._path):
                existed, entry = await self.cache.get_or_create(
                    uri=p.resolve().as_uri(),
                    contents=p.read_bytes,
                    metadata={
                        "step": "fetching",
                        "format": p.suffix[1:],
                        "strategy": PathFetcher.supported,
                    },
                )
                self.results.append(entry.path)
                yield Event(
                    Event.Type.PROGRESS,
                    (
                        ("Cached" if existed else "Copied")
                        + f" local path {p.resolve().as_uri()}"
                    ),
                )

        except Exception as e:
            yield Event(Event.Type.EXCEPTION, f"ERROR: {e}")

    @override
    def completed_callback(self) -> Event:
        return Event(Event.Type.COMPLETED, "Completed local path copy")
