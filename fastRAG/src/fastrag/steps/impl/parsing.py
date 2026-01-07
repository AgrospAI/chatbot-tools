import asyncio
from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Dict, List, override

from fastrag.cache.cache import ICache
from fastrag.cache.filters import MetadataFilter
from fastrag.config.config import Parsing
from fastrag.events import Event
from fastrag.helpers.filters import OrFilter
from fastrag.plugins import PluginRegistry, plugin
from fastrag.steps.step import IStep
from fastrag.steps.task import Task
from fastrag.systems import System


@dataclass
@plugin(system=System.STEP, supported="parsing")
class ParsingStep(IStep):

    description: ClassVar[str] = "PARSE"
    step: list[Parsing]

    @override
    async def get_tasks(
        self,
        cache: ICache,
    ) -> Dict[Task, List[AsyncGenerator[Event, None]]]:
        tasks = {}
        for s in self.step:
            instance = PluginRegistry.get_instance(
                System.PARSING, s.strategy, cache=cache, **s.params
            )
            entries = await cache.get_entries(
                instance.filter
                & OrFilter(
                    [MetadataFilter(strategy=strat) for strat in s.params["use"]]
                )
            )

            tasks[instance] = [instance.callback(uri, entry) for uri, entry in entries]

        return tasks

        # classes = [PluginRegistry.get(System.PARSING, s.strategy) for s in self.step]
        # entries = await asyncio.gather(*(cache.get_entries(c.filter) for c in classes))
        # instances = [c(cache=cache, **self.step) for c in classes]
        # return {
        #     task: [task.callback(uri, entry) for uri, entry in entries_]
        #     for entries_, task in zip(entries, instances)
        # }
