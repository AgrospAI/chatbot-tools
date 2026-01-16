from dataclasses import dataclass
from typing import ClassVar, override

from fastrag.steps.step import IStep, Tasks


@dataclass
class BenchmarkingStep(IStep):
    supported: ClassVar[str] = "benchmarking"
    description: ClassVar[str] = "BENCH"

    @override
    async def get_tasks(self) -> Tasks:
        for task in self.tasks:
            yield (task, [task.run()])
