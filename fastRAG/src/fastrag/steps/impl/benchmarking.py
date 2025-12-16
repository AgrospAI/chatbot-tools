from dataclasses import dataclass
from typing import ClassVar, Generator, Iterable, override

from fastrag.benchmarking.benchmarker import BenchmarkingEvent
from fastrag.config.config import Benchmarking
from fastrag.steps.steps import IStepRunner


@dataclass(frozen=True)
class BenchmarkingStep(IStepRunner):

    step: list[Benchmarking]
    description: ClassVar[str] = "BENCH"

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["benchmarking"]

    @override
    def run(self) -> Generator[BenchmarkingEvent, None, None]: ...

    @override
    def _log_verbose(self, event: BenchmarkingEvent) -> None:
        match event.type:
            case BenchmarkingEvent.Type.PROGRESS:
                self.progress.log(event.data)
            case BenchmarkingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case BenchmarkingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")

    @override
    def _log(self, event: BenchmarkingEvent) -> None:
        match event.type:
            case BenchmarkingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case BenchmarkingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
