from dataclasses import dataclass
from typing import Generator, Iterable, override

from fastrag.config.config import Benchmarking
from fastrag.steps.steps import IStepRunner


@dataclass(frozen=True)
class BenchmarkingStep(IStepRunner):

    step: list[Benchmarking]

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["benchmarking"]

    @override
    async def run_step(self) -> None: ...
