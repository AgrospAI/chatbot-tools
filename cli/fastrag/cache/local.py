import asyncio
import hashlib
import inspect
import json
import shutil
from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import ClassVar, Iterable, override

import aiofiles

from fastrag.cache.cache import CacheEntry, ContentsCallable, ICache
from fastrag.cache.filters import Filter
from fastrag.cache.utils import PosixTimestamp, timestamp

type Metadata = dict[str, CacheEntry]


def is_outdated(time: PosixTimestamp, lifespan: int) -> bool:
    return time + lifespan < timestamp()


@dataclass(frozen=True)
class Paths:
    metadata: Path = field(init=False, repr=False)
    data: Path = field(init=False, repr=False)

    base: InitVar[Path]

    def __post_init__(self, base: Path) -> None:
        object.__setattr__(self, "metadata", base / "metadata.json")
        object.__setattr__(self, "data", base / "cache")

        self.metadata.parent.mkdir(exist_ok=True)
        self.data.mkdir(exist_ok=True)

        self.metadata.touch(mode=0o770, exist_ok=True)


@dataclass
class LocalCache(ICache):
    base: ClassVar[Path] = Path(".fastrag")
    supported: ClassVar[str] = "local"

    _dirty: bool = field(init=False, default=False, repr=False)
    _paths: Paths = field(init=False, repr=False)
    _lock: asyncio.Lock = field(init=False, repr=False, default_factory=asyncio.Lock)
    metadata: Metadata = field(init=False, repr=False, default_factory=lambda: dict)

    def __post_init__(self) -> None:
        # Load metadata from file
        metadata = {}

        paths = Paths(self.base)

        raw = paths.metadata.read_text()
        if raw:
            raw = json.loads(raw)
            metadata = {k: CacheEntry.from_dict(v) for k, v in raw.items()}

        self._paths = paths
        self.metadata = metadata

        self._delete_invalid()

    @override
    def is_present(self, uri: str) -> bool:
        entry = self.metadata.get(uri, None)
        return entry is not None and not is_outdated(entry.timestamp, self.lifespan)

    @override
    async def create(
        self,
        uri: str,
        contents: bytes,
        metadata: dict | None = None,
    ) -> CacheEntry:
        digest = hashlib.sha256(uri.encode()).hexdigest()
        entry = CacheEntry(
            path=self._paths.data / digest,
            metadata=metadata,
        )

        async with self._lock:
            self.metadata[uri] = entry
            await self._save(entry.path, contents)
            self._dirty = True

        return entry

    @override
    async def get_or_create(
        self,
        uri: str,
        contents: ContentsCallable,
        metadata: dict | None = None,
    ) -> tuple[bool, CacheEntry]:
        entry = await self.get(uri)
        if entry:
            # If metadata.experiment is present, update it !
            experiment = metadata.get("experiment", None)
            if experiment and experiment is not entry.metadata["experiment"]:
                cached = self.metadata[uri]
                cached.metadata["experiment"] = experiment
                self.metadata[uri] = cached
                self._dirty = True

            return True, entry

        result = contents()
        if inspect.isawaitable(result):
            data = await result
        else:
            data = result

        return False, await self.create(uri, data, metadata)

    @override
    async def get(self, uri: str) -> CacheEntry | None:
        return self.metadata.get(uri) if self.is_present(uri) else None

    @override
    async def get_entries(
        self, filter: Filter | None = None
    ) -> Iterable[tuple[str, CacheEntry]]:
        if not filter:
            return [(k, e) for k, e in self.metadata.items()]
        return [(k, e) for k, e in self.metadata.items() if filter.apply(e)]

    @override
    def clean(self) -> int:
        paths = self.base.rglob("*")
        size = sum(p.stat().st_size for p in paths if p.is_file())
        shutil.rmtree(self.base)
        return size

    @override
    async def flush(self) -> None:
        async with self._lock:
            if not self._dirty:
                return
            raw = {k: v.to_dict() for k, v in self.metadata.items()}
            with open(self._paths.metadata, "w") as f:
                json.dump(raw, f, indent=2)
            self._dirty = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.flush()

    async def autosave(self, interval: int = 5):
        while True:
            await asyncio.sleep(interval)
            await self.flush()

    def _delete_invalid(self) -> None:
        outdated = [
            (h, v.path)
            for h, v in self.metadata.items()
            if is_outdated(v.timestamp, self.lifespan)
        ]
        if not outdated:
            return

        for h, item in outdated:
            item.unlink(missing_ok=True)
            self.metadata.pop(h)

        self._dirty = True

    async def _save(self, path: Path, content: bytes) -> None:
        async with aiofiles.open(path, "wb+") as f:
            await f.write(content)
