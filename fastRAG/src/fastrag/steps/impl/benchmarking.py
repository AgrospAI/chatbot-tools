from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, List, override

from fastrag.config.config import Benchmarking
from fastrag.events import Event
from fastrag.plugins import plugin
from fastrag.steps.benchmarking import BenchmarkingEvent
from fastrag.steps.step import IStep
from fastrag.systems import System


@dataclass(frozen=True)
@plugin(system=System.STEP, supported="benchmarking")
class BenchmarkingStep(IStep):

    step: list[Benchmarking]
    description: ClassVar[str] = "BENCH"

    @override
    def get_tasks(self) -> List[AsyncGenerator[Event, None]]:
        return []

    @override
    def log_verbose(self, event: BenchmarkingEvent) -> None:
        match event.type:
            case BenchmarkingEvent.Type.PROGRESS:
                self.progress.log(event.data)
            case BenchmarkingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case BenchmarkingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
            case _:
                self.progress.log(f"[red]:?: UNEXPECTED EVENT: {event}[/red]")

    @override
    def log(self, event: BenchmarkingEvent) -> None:
        match event.type:
            case BenchmarkingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case BenchmarkingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
            case _:
                self.progress.log(f"[red]:?: UNEXPECTED EVENT: {event}[/red]")
