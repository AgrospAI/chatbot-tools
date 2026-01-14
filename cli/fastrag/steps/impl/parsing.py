from dataclasses import dataclass
from typing import ClassVar, override

from fastrag.cache.filters import MetadataFilter
from fastrag.helpers.filters import OrFilter
from fastrag.steps.step import IStep


@dataclass
class ParsingStep(IStep):
    supported: ClassVar[str] = "parsing"
    description: ClassVar[str] = "PARSE"

    @override
    async def get_tasks(self):
        for idx, task in enumerate(self._tasks):
            params = self.step[idx].params
            entries = await self.cache.get_entries(
                task.filter
                & OrFilter([MetadataFilter(strategy=strat) for strat in params["use"]])
            )
            yield (task, [task.run(uri, entry) for uri, entry in entries])
