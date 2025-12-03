from typing import Protocol, TypeVar

from fastrag.data import Data

T = TypeVar("T")


class Fetcher(Protocol[T]):
    """
    Base protocol for the classes that implement the fetch process.
    """

    def fetch(self) -> Data[T]: ...
