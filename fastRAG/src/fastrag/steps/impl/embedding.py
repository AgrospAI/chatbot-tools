from dataclasses import dataclass
from typing import Iterable, override

from fastrag.config.config import Embedding
from fastrag.steps.steps import IStepRunner


@dataclass(frozen=True)
class EmbeddingStep(IStepRunner):

    step: list[Embedding]

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["embedding"]

    @override
    async def run_step(self) -> None: ...
