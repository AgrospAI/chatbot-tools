from dataclasses import dataclass, field, fields
from pathlib import Path
from urllib.parse import unquote, urlparse

import aiofiles

from fastrag.cache.utils import PosixTimestamp, timestamp


@dataclass(frozen=True)
class CacheEntry:
    path: Path
    timestamp: PosixTimestamp = field(default_factory=timestamp)
    metadata: dict = field(default_factory=dict)

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
        content = self._content
        if content is None:
            async with aiofiles.open(self.path, "rb") as f:
                content: bytes = await f.read()
            object.__setattr__(self, "_content", content)
        return content
