from dataclasses import dataclass
from pathlib import Path

from fastrag.data import Data
from fastrag.fetchers.fetcher import Fetcher


@dataclass(frozen=True)
class Text(Fetcher[list[str]]):

    path: Path
    """Path to read the text from"""

    encoding: str = "utf-8"
    """Encoding of the file to read"""

    def fetch(self) -> Data[list[str]]:
        with open(self.path, "r", encoding=self.encoding) as f:
            return Data(content=f.readlines())
