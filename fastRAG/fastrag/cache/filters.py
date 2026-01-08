from dataclasses import dataclass, field
from typing import override

from fastrag.cache.cache import CacheEntry
from fastrag.config.config import StepNames
from fastrag.helpers.filters import Filter


@dataclass
class StepFilter(Filter[CacheEntry]):
    step: StepNames

    @override
    def apply(self, entry: CacheEntry) -> bool:
        return entry.step == self.step


@dataclass(kw_only=True, slots=True)
class MetadataFilter(Filter[CacheEntry]):
    criteria: dict[str, any] = field(init=False)

    def __init__(self, **kwargs) -> None:
        self.criteria = kwargs

    @override
    def apply(self, entry: CacheEntry) -> bool:
        if not entry.metadata:
            return False
        for key, expected in self.criteria.items():
            if entry.metadata.get(key) != expected:
                return False
        return True
