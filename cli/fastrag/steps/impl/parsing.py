from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Dict, List, override

from fastrag.cache.cache import ICache
from fastrag.cache.filters import MetadataFilter
from fastrag.config.config import Parsing
from fastrag.events import Event
from fastrag.helpers.filters import OrFilter
from fastrag.plugins import PluginRegistry, inject
from fastrag.steps.step import IStep
from fastrag.steps.task import Task


@dataclass
class ParsingStep(IStep):
    supported: ClassVar[str] = "parsing"
    description: ClassVar[str] = "PARSE"

    step: list[Parsing]

    @override
    async def get_tasks(
        self,
        cache: ICache,
    ) -> Dict[Task, List[AsyncGenerator[Event, None]]]:
        tasks = {}
        for s in self.step:
            instance = inject(Task, s.strategy, cache=cache, **s.params)
            entries = await cache.get_entries(
                instance.filter
                & OrFilter([MetadataFilter(strategy=strat) for strat in s.params["use"]])
            )

            tasks[instance] = [instance.callback(uri, entry) for uri, entry in entries]

        return tasks
