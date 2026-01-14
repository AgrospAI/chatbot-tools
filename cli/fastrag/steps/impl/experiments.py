from dataclasses import dataclass
from typing import ClassVar, override

from fastrag.steps.step import IMultiStep


@dataclass
class ExperimentsStep(IMultiStep):
    supported: ClassVar[str] = "experiments"
    description: ClassVar[str] = "EXPERIMENTS"

    @override
    async def get_tasks(self):
        for task in self._tasks:
            async for task, generators in task.get_tasks():
                yield task, generators
