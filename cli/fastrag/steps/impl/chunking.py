from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Dict, override

from fastrag.cache.cache import ICache
from fastrag.config.config import Chunking
from fastrag.events import Event
from fastrag.plugins import plugin
from fastrag.steps.step import IStep
from fastrag.steps.task import Task
from fastrag.systems import System


@dataclass
@plugin(system=System.STEP, supported="chunking")
class ChunkingStep(IStep):
    description: ClassVar[str] = "CHUNK"
    step: list[Chunking]

    @override
    async def get_tasks(self, cache: ICache) -> Dict[Task, AsyncGenerator[Event, None]]:
        return {}
