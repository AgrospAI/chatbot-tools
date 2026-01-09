from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, Dict, override

from fastrag.cache.cache import ICache
from fastrag.config.config import Embedding
from fastrag.events import Event
from fastrag.steps.step import IStep
from fastrag.steps.task import Task


@dataclass
class EmbeddingStep(IStep):
    description: ClassVar[str] = "EMBED"
    supported: ClassVar[str] = "embedding"

    step: list[Embedding]

    @override
    async def get_tasks(self, cache: ICache) -> Dict[Task, AsyncGenerator[Event, None]]:
        return {}
