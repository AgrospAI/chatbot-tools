from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Dict, override

from fastrag.cache.cache import ICache
from fastrag.events import Event
from fastrag.steps.step import IStep
from fastrag.steps.task import Task


@dataclass
class BenchmarkingStep(IStep):
    supported: ClassVar[str] = "benchmarking"
    description: ClassVar[str] = "BENCH"

    @override
    async def get_tasks(self, cache: ICache) -> Dict[Task, AsyncGenerator[Event, None]]:
        return {}
