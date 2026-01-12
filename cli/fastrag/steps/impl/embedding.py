from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, override

from fastrag.cache.cache import ICache
from fastrag.events import Event
from fastrag.plugins import inject
from fastrag.steps.step import IStep
from fastrag.steps.task import Task


@dataclass
class EmbeddingStep(IStep):
    description: ClassVar[str] = "EMBED"
    supported: ClassVar[str] = "embedding"

    @override
    async def get_tasks(self, cache: ICache) -> dict[Task, list[AsyncGenerator[Event, None]]]:
        tasks = {}
        for s in self.step:
            instance = inject(Task, s.strategy, cache=cache, **s.params)
            entries = await cache.get_entries(instance.filter)
            tasks[instance] = [instance.callback(uri, entry) for uri, entry in entries]

        return tasks
