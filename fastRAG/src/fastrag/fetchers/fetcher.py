from typing import Generic, TypeVar

from fastrag.data import Data
from fastrag.plugins.base import BasePlugin

T = TypeVar("T")


class Fetcher(BasePlugin, Generic[T]):
    """
    Base protocol for the classes that implement the fetch process.
    """

    def fetch(self) -> Data[T]:
        raise NotImplementedError
