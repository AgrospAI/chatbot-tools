from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generic, TypeVar, override

from fastrag.cache.entry import CacheEntry

T = TypeVar("T")


@dataclass
class Filter(Generic[T], ABC):
    """General purpose filter"""

    @abstractmethod
    def apply(self, entry: T) -> bool:
        """Apply filter to entry

        Args:
            entry (T): entry to filter

        Returns:
            bool: if the entry passes the filter
        """

        raise NotImplementedError

    def __and__(self, other: Filter[T]):
        return AndFilter([self, other])

    def __or__(self, other: Filter[T]):
        return OrFilter([self, other])


@dataclass
class AndFilter(Filter[T]):
    filters: list[Filter[T]]

    @override
    def apply(self, entry: T) -> bool:
        if not self.filters:
            return False
        return all(f.apply(entry) for f in self.filters)


@dataclass
class OrFilter(Filter[T]):
    filters: list[Filter[T]]

    @override
    def apply(self, entry: T) -> bool:
        if not self.filters:
            return True
        return any(f.apply(entry) for f in self.filters)


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
