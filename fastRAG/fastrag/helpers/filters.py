from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar, override

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

    def __and__(self, other: Filter):
        return AndFilter([*self.filters, other])

    def __or__(self, other: Filter):
        return OrFilter([*self.filters, other])


@dataclass
class OrFilter(Filter[T]):
    filters: list[Filter[T]]

    @override
    def apply(self, entry: T) -> bool:
        if not self.filters:
            return True
        return any(f.apply(entry) for f in self.filters)

    def __and__(self, other: Filter):
        return AndFilter([*self.filters, other])

    def __or__(self, other: Filter):
        return OrFilter([*self.filters, other])
