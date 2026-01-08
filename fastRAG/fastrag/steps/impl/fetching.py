from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Dict, override

from fastrag.cache.cache import ICache
from fastrag.config.config import Source
from fastrag.events import Event
from fastrag.plugins import PluginRegistry, plugin
from fastrag.steps.step import IStep
from fastrag.steps.task import Task
from fastrag.systems import System


@dataclass
@plugin(system=System.STEP, supported="fetching")
class SourceStep(IStep):
    description: ClassVar[str] = "FETCH"
    step: list[Source]

    @override
    async def get_tasks(self, cache: ICache) -> Dict[Task, AsyncGenerator[Event, None]]:
        return {
            inst: [inst.callback()]
            for inst in [
                PluginRegistry.get_instance(
                    System.FETCHING, s.strategy, cache=cache, **s.params
                )
                for s in self.step
            ]
        }
