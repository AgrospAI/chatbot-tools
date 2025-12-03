from dataclasses import dataclass
from pathlib import Path

from fastrag.data import Data
from fastrag.fetchers import Fetcher, Text


@dataclass(frozen=True)
class Directory:

    path: Path
    """Path of the folder to fetch"""

    fetcher: Fetcher[list[str]] = Text
    """Fetcher to use in the individual files"""

    recurse: bool = False
    """If it should fetch the subdirectories"""

    def fetch(self) -> Data[dict[Path, list[str]]]: ...
