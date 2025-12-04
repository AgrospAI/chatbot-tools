from pathlib import Path
from typing import Iterable, override
from fastrag.config.config import Chunking


class RecursiveTextSplitter(Chunking):

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["RecursiveTextSplitter"]

    @classmethod
    def chunk(cls, path: Path) -> None:
        print("Hello RecursiveTextSplitter")
