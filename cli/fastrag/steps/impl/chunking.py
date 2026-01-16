from dataclasses import dataclass
from typing import ClassVar, override

from fastrag.steps.step import IStep, Tasks


@dataclass
class ChunkingStep(IStep):
    supported: ClassVar[str] = "chunking"
    description: ClassVar[str] = "CHUNK"

    @override
    async def get_tasks(self) -> Tasks:
        for task in self.tasks:
            entries = await self.resources.cache.get_entries(task.filter)
            yield (task, [task.run(uri, entry) for uri, entry in entries])
