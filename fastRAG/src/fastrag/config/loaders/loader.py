from typing import IO, Protocol

from fastrag.config import Config


class Loader(Protocol):

    def load(self, fp: IO[str]) -> Config: ...
