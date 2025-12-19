from dataclasses import dataclass
from typing import AsyncGenerator, Callable, ClassVar, Dict, List, override

from fastrag.cache.cache import ICache
from fastrag.config.config import Source
from fastrag.events import Event
from fastrag.plugins import PluginRegistry, plugin
from fastrag.steps.fetchers.events import FetchingEvent
from fastrag.steps.step import IStep
from fastrag.steps.task import Task
from fastrag.systems import System


@dataclass
@plugin(system=System.STEP, supported="fetching")
class SourceStep(IStep):

    description: ClassVar[str] = "FETCH"
    step: list[Source]

    @override
    def get_instances(
        self,
        const: List[Callable[[any], Task]],
        cache: ICache,
    ) -> List[Task]:
        return [c(cache=cache, **s.params) for c, s in zip(const, self.step)]

    @override
    async def get_tasks(self, cache: ICache) -> Dict[Task, AsyncGenerator[Event, None]]:
        return {
            inst: [inst.callback()]
            for inst in self.get_instances(
                [PluginRegistry.get(System.FETCHING, s.strategy) for s in self.step],
                cache,
            )
        }

    @override
    def log_verbose(self, event: FetchingEvent) -> None:
        match event.type:
            case FetchingEvent.Type.PROGRESS:
                self.progress.log(event.data)
            case FetchingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case FetchingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
            case _:
                self.progress.log(f"[red]:?: UNEXPECTED EVENT: {event}[/red]")

    @override
    def log_normal(self, event: FetchingEvent) -> None:
        match event.type:
            case FetchingEvent.Type.PROGRESS:
                ...
            case _:
                self.log_verbose(event)
