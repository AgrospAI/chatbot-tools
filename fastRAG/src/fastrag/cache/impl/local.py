import hashlib
import json
import os
from asyncio import Lock
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, get_args, override

from fastrag.cache.cache import CacheEntry, CacheSection, ICache

type Metadata = dict[str, CacheEntry]


@dataclass(frozen=True)
class LocalCache(ICache):

    _lock: Lock = field(init=False, repr=False, default_factory=Lock)
    metadata: Metadata = field(init=False)

    def __post_init__(self) -> None:
        # Load metadata from file
        metadata = {}

        if self.metadata_path.exists():
            with open(self.metadata_path, "r") as f:
                raw = json.load(f)
                metadata = {k: CacheEntry.from_dict(v) for k, v in raw.items()}

        for section in get_args(CacheSection):
            os.makedirs(self.base / section, exist_ok=True)

        object.__setattr__(self, "metadata", metadata)

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["local"]

    @property
    def metadata_path(self) -> Path:
        return self.base / "metadata.json"

    @override
    def is_present(self, uri: str) -> bool:
        entry = self.get(uri)
        return entry is not None and not self.is_outdated(entry.timestamp)

    @override
    def hash(self, content: str) -> str:
        return hashlib.sha256(content).hexdigest()

    @override
    async def store(
        self,
        uri: str,
        contents: bytes,
        section: CacheSection,
        metadata: dict | None = None,
    ) -> CacheEntry:
        digest = self.hash(contents)
        entry = CacheEntry(
            content_hash=digest,
            path=self.base / section / digest,
            metadata=metadata,
            section=section,
        )
        async with self._lock:
            self.metadata[uri] = entry
            self._save(entry.path, contents)
        return entry

    @override
    async def get(self, uri: str) -> CacheEntry | None:
        return self.metadata.get(uri, None)

    def _save(self, path: Path, contents: bytes):
        self.metadata_path.touch(mode=0o770, exist_ok=True)
        raw = {k: v.to_dict() for k, v in self.metadata.items()}
        with open(self.metadata_path, "w") as f:
            json.dump(raw, f, indent=2)
        with open(path, "wb") as f:
            f.write(contents)
