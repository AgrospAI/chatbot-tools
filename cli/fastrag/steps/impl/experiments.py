from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Dict, List, override

from fastrag.cache.cache import ICache
from fastrag.events import Event
from fastrag.plugins import inject
from fastrag.steps.step import IStep
from fastrag.steps.task import Task


@dataclass
class ExperimentsStep(IStep):
    supported: ClassVar[str] = "experiments"
    description: ClassVar[str] = "EXPERIMENTS"

    @override
    async def get_tasks(self, cache: ICache) -> Dict[Task, List[AsyncGenerator[Event, None]]]:
        tasks = {}

        for step in self.step:
            instance = inject(Task, step.strategy, cache=cache, **step.params)
            entries = await cache.get_entries(getattr(instance, "filter", None))
            tasks[instance] = [instance.callback(uri, entry) for uri, entry in entries]

        return tasks
