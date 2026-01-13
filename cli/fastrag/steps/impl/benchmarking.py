from dataclasses import dataclass
from typing import ClassVar, override

from fastrag.steps.step import IStep


@dataclass
class BenchmarkingStep(IStep):
    supported: ClassVar[str] = "benchmarking"
    description: ClassVar[str] = "BENCH"

    @override
    async def get_tasks(self):
        for task in self._tasks:
            yield (task, [task.run()])
