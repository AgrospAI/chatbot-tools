from __future__ import annotations

from dataclasses import asdict, dataclass, field
from functools import cached_property
from pathlib import Path
from urllib.parse import unquote, urlparse

from fastrag.config.config import StepNames
from fastrag.helpers.utils import PosixTimestamp, timestamp


@dataclass(frozen=True)
class CacheEntry:
    content_hash: str
    step: StepNames
    path: Path
    timestamp: PosixTimestamp = field(default_factory=timestamp)
    metadata: dict | None = field(default=None)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["path"] = str(self.path.resolve().as_uri())
        return d

    @staticmethod
    def from_dict(d: dict) -> CacheEntry:
        d = dict(d)
        parsed = urlparse(d["path"])
        d["path"] = Path(unquote(parsed.path))
        return CacheEntry(**d)

    @cached_property
    def content(self) -> bytes:
        return self.path.read_bytes()
