from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Dict, override

from fastrag.cache.cache import ICache
from fastrag.config.config import Benchmarking
from fastrag.events import Event
from fastrag.plugins import plugin
from fastrag.steps.benchmarking import BenchmarkingEvent
from fastrag.steps.step import IStep
from fastrag.steps.task import Task
from fastrag.systems import System


@dataclass
@plugin(system=System.STEP, supported="benchmarking")
class BenchmarkingStep(IStep):

    step: list[Benchmarking]
    description: ClassVar[str] = "BENCH"

    @override
    async def get_tasks(self, cache: ICache) -> Dict[Task, AsyncGenerator[Event, None]]:
        return {}

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
    def log_normal(self, event: BenchmarkingEvent) -> None:
        match event.type:
            case BenchmarkingEvent.Type.PROGRESS:
                ...
            case _:
                self.log_verbose(event)
