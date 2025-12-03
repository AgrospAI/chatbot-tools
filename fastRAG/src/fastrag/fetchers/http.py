from dataclasses import dataclass

from fastrag.data import Data
from fastrag.fetchers.fetcher import Fetcher


@dataclass(frozen=True)
class Http(Fetcher[list[str]]):

    source: str

    def fetch(self) -> Data[list[str]]: ...
