from dataclasses import dataclass, field, fields
from pathlib import Path
from urllib.parse import unquote, urlparse

import aiofiles

from fastrag.cache.utils import PosixTimestamp, timestamp


@dataclass(frozen=True)
class CacheEntry:
    path: Path
    timestamp: PosixTimestamp = field(default_factory=timestamp)
    metadata: dict | None = field(default=None)

    _content: bytes | None = field(default=None, init=False, repr=False, compare=False)

    def to_dict(self) -> dict:
        return {
            f.name: getattr(self, f.name) for f in fields(self) if not f.name.startswith("_")
        } | {"path": str(self.path.resolve().as_uri())}

    @staticmethod
    def from_dict(d: dict) -> "CacheEntry":
        d = dict(d)
        parsed = urlparse(d["path"])
        d["path"] = Path(unquote(parsed.path))
        return CacheEntry(**d)

    @property
    def content(self) -> bytes:
        return self.path.read_bytes()

    async def get_content(self) -> bytes:
        if self._content is None:
            async with aiofiles.open(self.path, "rb") as f:
                object.__setattr__(self, "_content", await f.read())
        return self._content
