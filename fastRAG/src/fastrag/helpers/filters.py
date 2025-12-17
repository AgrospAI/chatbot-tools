from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar, override

T = TypeVar("T")


@dataclass
class Filter(Generic[T], ABC):

    @abstractmethod
    def apply(self, entry: T) -> bool: ...

    def __or__(self, other: Filter[T]):
        return MultiFilter([self, other])


@dataclass
class MultiFilter(Filter[T]):

    filters: list[Filter[T]]

    @override
    def apply(self, entry: T) -> bool:
        return all(f.apply(entry) for f in self.filters)

    def __or__(self, other: Filter):
        return MultiFilter([*self.filters, other])


@dataclass
class OrFilter(Filter[T]):

    filters: list[Filter[T]]

    def __init__(self, *args) -> None:
        self.filters = [*args]

    @override
    def apply(self, entry: T) -> bool:
        return any(f.apply(entry) for f in self.filters)
