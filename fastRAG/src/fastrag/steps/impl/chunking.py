from dataclasses import dataclass
from typing import Generator, Iterable, override

from fastrag.config.config import Chunking
from fastrag.steps.steps import StepRunner


@dataclass(frozen=True)
class ChunkingStep(StepRunner):

    step: list[Chunking]

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["chunking"]

    @override
    def run_step(self) -> Generator[None, None, None]:
        for step in self.step:
            yield
