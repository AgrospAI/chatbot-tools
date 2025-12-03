from dataclasses import dataclass
from typing import IO

from fastrag.config import Config


@dataclass(frozen=True)
class YamlLoader:

    def load(self, fp: IO[str]) -> Config: ...
