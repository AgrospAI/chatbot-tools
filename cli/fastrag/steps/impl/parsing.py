from dataclasses import dataclass
from typing import ClassVar, override

from fastrag.cache import CacheEntry, MetadataFilter
from fastrag.helpers.filters import Filter, OrFilter
from fastrag.steps.step import IStep, Tasks
from fastrag.steps.task import Task


@dataclass
class ParsingStep(IStep):
    supported: ClassVar[str] = "parsing"
    description: ClassVar[str] = "PARSE"

    @override
    async def get_tasks(self) -> Tasks:
        for idx, task in enumerate(self.tasks):
            extended_filter = self.get_extended_filter(idx, task)
            entries = await self.resources.cache.get_entries(extended_filter)
            yield (task, [task.run(uri, entry) for uri, entry in entries])

    def get_extended_filter(self, index: int, task: Task) -> Filter[CacheEntry]:
        params = self.tasks[index]
        return task.filter & OrFilter([MetadataFilter(strategy=s) for s in params.use])
