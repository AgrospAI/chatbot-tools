import hashlib
import json
from asyncio import Lock
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, get_args, override

from fastrag.cache.cache import CacheEntry, ICache, StepNames
from fastrag.helpers import PosixTimestamp, timestamp
from fastrag.helpers.filters import Filter
from fastrag.plugins import plugin
from fastrag.systems import System

type Metadata = dict[str, CacheEntry]


def is_outdated(time: PosixTimestamp, lifespan: int) -> bool:
    return time + lifespan < timestamp()


@dataclass(frozen=True)
@plugin(system=System.CACHE, supported="local")
class LocalCache(ICache):
    _lock: Lock = field(init=False, repr=False, default_factory=Lock)
    metadata: Metadata = field(init=False, repr=False, default_factory=lambda: dict)

    def __post_init__(self) -> None:
        # Load metadata from file
        metadata = {}

        if self.metadata_path.exists():
            with open(self.metadata_path, "r") as f:
                raw = json.load(f)
                metadata = {k: CacheEntry.from_dict(v) for k, v in raw.items()}

        for step in get_args(StepNames):
            path: Path = self.base / step
            path.mkdir(parents=True, exist_ok=True)

        object.__setattr__(self, "metadata", metadata)

        self._delete_invalid()

    @property
    def metadata_path(self) -> Path:
        return self.base / "metadata.json"

    @override
    def is_present(self, uri: str) -> bool:
        entry = self.metadata.get(uri, None)
        return entry is not None and not is_outdated(entry.timestamp, self.lifespan)

    @override
    async def create(
        self,
        uri: str,
        contents: bytes,
        step: StepNames,
        metadata: dict | None = None,
    ) -> CacheEntry:
        digest = hashlib.sha256(contents).hexdigest()
        entry = CacheEntry(
            content_hash=digest,
            path=self.base / step / digest,
            metadata=metadata,
            step=step,
        )
        async with self._lock:
            self.metadata[uri] = entry
            self._save(entry.path, contents)
            self._save_metadata()
        return entry

    @override
    async def get_or_create(
        self,
        uri: str,
        contents: Callable[..., bytes],
        step: StepNames,
        metadata: dict | None = None,
    ) -> tuple[bool, CacheEntry]:
        entry = await self.get(uri)
        if entry:
            return True, entry
        return False, await self.create(uri, contents(), step, metadata)

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
        self._save_metadata()

    def _save_metadata(self) -> None:
        self.metadata_path.touch(mode=0o770, exist_ok=True)
        raw = {k: v.to_dict() for k, v in self.metadata.items()}
        with open(self.metadata_path, "w") as f:
            json.dump(raw, f, indent=2)

    def _save(self, path: Path, contents: bytes) -> None:
        with open(path, "wb") as f:
            f.write(contents)
