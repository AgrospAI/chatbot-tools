from dataclasses import dataclass
from typing import ClassVar, override

from fastrag.cache.filters import MetadataFilter
from fastrag.steps.step import IStep, Tasks


@dataclass
class EmbeddingStep(IStep):
    supported: ClassVar[str] = "embedding"
    description: ClassVar[str] = "EMBED"

    @property
    def filter(self):
        return MetadataFilter(experiment=self.experiment.hash)

    @override
    async def get_tasks(self) -> Tasks:
        for task in self.tasks:
            entries = await self.resources.cache.get_entries(self.filter & task.filter)

            yield (task, [task.run(uri, entry) for uri, entry in entries])
