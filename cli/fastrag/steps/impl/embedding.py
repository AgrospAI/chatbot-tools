from dataclasses import dataclass
from typing import ClassVar, override

from fastrag.steps.step import IStep, Tasks


@dataclass
class EmbeddingStep(IStep):
    supported: ClassVar[str] = "embedding"
    description: ClassVar[str] = "EMBED"

    @override
    async def get_tasks(self) -> Tasks:
        for task in self._tasks:
            entries = await self.cache.get_entries(task.filter)
            yield (task, [task.run(uri, entry) for uri, entry in entries])

        # Upload embeddings
        # self.resources.store.add_documents()
