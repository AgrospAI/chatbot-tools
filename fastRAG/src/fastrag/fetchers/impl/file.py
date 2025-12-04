from pathlib import Path
from typing import Iterable, override

from fastrag.fetchers.fetcher import Fetcher


class FileFetcher(Fetcher):

    @classmethod
    @override
    def fetch(cls, value: str) -> Iterable[Path]:
        path = Path(value)

        if not path or not path.exists():
            raise FileNotFoundError(f"Can't find source file path {path}")

        if not path.is_file():
            raise ValueError("Given path is not a file")

        return
