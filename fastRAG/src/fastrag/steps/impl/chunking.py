from dataclasses import dataclass
from typing import Iterable, override

from fastrag.config.config import Chunking
from fastrag.steps.steps import IStepRunner


@dataclass(frozen=True)
class ChunkingStep(IStepRunner):

    step: list[Chunking]

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["chunking"]

    @override
    async def run_step(self) -> None: ...
