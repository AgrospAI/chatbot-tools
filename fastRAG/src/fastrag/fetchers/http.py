from dataclasses import dataclass

from fastrag.data import Data


@dataclass(frozen=True)
class HTTP:

    source: str

    def fetch(self) -> Data[list[str]]: ...
