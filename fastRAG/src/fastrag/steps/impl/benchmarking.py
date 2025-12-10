from dataclasses import dataclass
from typing import Generator, Iterable, override

from fastrag.config.config import Benchmarking
from fastrag.steps.steps import StepRunner


@dataclass(frozen=True)
class BenchmarkingStep(StepRunner):

    step: list[Benchmarking]

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["benchmarking"]

    @override
    async def run_step(self) -> None: ...
