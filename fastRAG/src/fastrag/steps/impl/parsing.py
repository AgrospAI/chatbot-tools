import asyncio
from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Dict, List, override

from fastrag.cache.cache import ICache
from fastrag.config.config import Parsing
from fastrag.events import Event
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
        classes = [PluginRegistry.get(System.PARSING, s.strategy) for s in self.step]
        entries = await asyncio.gather(*(cache.get_entries(c.filter) for c in classes))
        for c, entries_ in zip(classes, entries):
            c.entries = entries_
        instances = [c(cache=cache) for c in classes]
        return {
            task: [task.callback(uri, entry) for uri, entry in entries_]
            for entries_, task in zip(entries, instances)
        }
