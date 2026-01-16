from dataclasses import dataclass
from typing import ClassVar, override

from fastrag.steps.step_group import IMultiStep


@dataclass
class ExperimentsStep(IMultiStep):
    supported: ClassVar[str] = "experiments"
    description: ClassVar[str] = "EXPERIMENTS"

    @override
    async def get_tasks(self):
        for step in self.steps.values():
            async for task, generators in step.get_tasks():
                yield task, generators
