from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Dict, override

from fastrag.cache.cache import ICache
from fastrag.events import Event
from fastrag.plugins import inject
from fastrag.steps.step import IStep
from fastrag.steps.task import Task


@dataclass
class SourceStep(IStep):
    description: ClassVar[str] = "FETCH"
    supported: ClassVar[str] = "fetching"

    @override
    async def get_tasks(self, cache: ICache) -> Dict[Task, AsyncGenerator[Event, None]]:
        return {
            inst: [inst.callback()]
            for inst in [inject(Task, s.strategy, cache=cache, **s.params) for s in self.step]
        }
