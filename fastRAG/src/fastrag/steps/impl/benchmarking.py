from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Generator, Iterable, override

from fastrag.benchmarking.events import BenchmarkingEvent
from fastrag.config.config import Benchmarking
from fastrag.plugins.base import plugin
from fastrag.steps.impl.arunner import IAsyncStepRunner


@dataclass(frozen=True)
@plugin(key="step", supported="benchmarking")
class BenchmarkingStep(IAsyncStepRunner):

    step: list[Benchmarking]
    description: ClassVar[str] = "BENCH"

    @override
    def run(self) -> Generator[BenchmarkingEvent, None, None]: ...

    @override
    def get_tasks(self) -> Iterable[AsyncGenerator[BenchmarkingEvent, None]]: ...

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
