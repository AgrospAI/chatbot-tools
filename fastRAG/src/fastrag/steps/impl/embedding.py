from dataclasses import dataclass
from typing import Generator, Iterable, override

from fastrag.config.config import Embedding
from fastrag.steps.steps import StepRunner


@dataclass(frozen=True)
class EmbeddingStep(StepRunner):

    step: list[Embedding]

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["embedding"]

    @override
    def run_step(self) -> Generator[None, None, None]:
        for step in self.step:
            yield
