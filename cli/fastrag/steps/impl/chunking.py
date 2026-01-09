from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Dict, override

from fastrag.cache.cache import ICache
from fastrag.config.config import Chunking
from fastrag.events import Event
from fastrag.steps.step import IStep
from fastrag.steps.task import Task


@dataclass
class ChunkingStep(IStep):
    description: ClassVar[str] = "CHUNK"
    supported: ClassVar[str] = "chunking"

    step: list[Chunking]

    @override
    async def get_tasks(self, cache: ICache) -> Dict[Task, AsyncGenerator[Event, None]]:
        tasks = {}
        for s in self.step:
            instance = PluginRegistry.get_instance(
                System.CHUNKING, s.strategy, cache=cache, **s.params
            )
            entries = await cache.get_entries(
                instance.filter
            )

            tasks[instance] = [instance.callback(uri, entry) for uri, entry in entries]

        return tasks