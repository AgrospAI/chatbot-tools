import asyncio
from dataclasses import dataclass
from typing import Iterable, override

from rich.console import Console

from fastrag.config.config import Source
from fastrag.fetchers.fetcher import Fetcher, FetcherEvent
from fastrag.steps.steps import StepRunner

console = Console()


@dataclass(frozen=True)
class SourceStep(StepRunner):

    step: list[Source]

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["sources"]

    @override
    async def run_step(self) -> None:
        fetchers = [
            Fetcher.get_supported_instance(source.strategy)(
                **source.params,
                cache=self.cache,
            ).fetch()
            for source in self.step
        ]
        tasks = [asyncio.create_task(fetcher.__anext__()) for fetcher in fetchers]

        while tasks:
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

            for d in done:
                try:
                    event: FetcherEvent = d.result()
                except StopAsyncIteration:
                    tasks.remove(d)
                    self.progress.advance(self.task_id)
                    continue

                match event.type:
                    case FetcherEvent.Type.PROGRESS:
                        self.progress.log(event.data)
                    case FetcherEvent.Type.EXCEPTION:
                        self.progress.log(f"[red]{event.data}[/red]")

                idx = tasks.index(d)
                tasks[idx] = asyncio.create_task(fetchers[idx].__anext__())
