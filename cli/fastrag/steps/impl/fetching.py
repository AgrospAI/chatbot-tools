from dataclasses import dataclass
from typing import ClassVar, override

from fastrag.steps.step import IStep, Tasks


@dataclass
class FetchingStep(IStep):
    supported: ClassVar[str] = "fetching"
    description: ClassVar[str] = "FETCH"

    @override
    async def get_tasks(self) -> Tasks:
        for task in self._tasks:
            yield (task, [task.run()])
