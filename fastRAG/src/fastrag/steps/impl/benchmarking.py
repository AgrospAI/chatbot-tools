from dataclasses import dataclass
from typing import ClassVar, Generator, Iterable, override

from fastrag.benchmarking.benchmarking import BenchmarkingEvent
from fastrag.config.config import Benchmarking
from fastrag.events import Event
from fastrag.steps.steps import IStepRunner


@dataclass(frozen=True)
class BenchmarkingStep(IStepRunner):

    step: list[Benchmarking]
    description: ClassVar[str] = "Running benchmarks"

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["benchmarking"]

    @override
    def run(self) -> Generator[BenchmarkingEvent, None, None]: ...

    @override
    def callback(self, event: Event) -> None: ...
