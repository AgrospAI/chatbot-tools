import asyncio
from dataclasses import dataclass
from typing import Iterable, override

from fastrag.config.config import Source
from fastrag.fetchers.fetcher import FetcherEvent, IFetcher
from fastrag.steps.steps import IStepRunner


@dataclass(frozen=True)
class SourceStep(IStepRunner):

    step: list[Source]

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["sources"]

    @override
    async def run_step(self) -> None:
        fetchers = [
            IFetcher.get_supported_instance(source.strategy)(
                **source.params,
                cache=self.cache,
            ).fetch()
            for source in self.step
        ]
        tasks = [asyncio.create_task(fetcher.__anext__()) for fetcher in fetchers]

        while tasks:
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

            for d in done:
                idx = tasks.index(d)

                try:
                    event: FetcherEvent = d.result()
                except StopAsyncIteration:
                    tasks.pop(idx)
                    fetchers.pop(idx)
                    self.progress.advance(self.task_id)
                    continue

                match event.type:
                    case FetcherEvent.Type.PROGRESS:
                        self.progress.log(event.data)
                    case FetcherEvent.Type.COMPLETED:
                        self.progress.log(
                            f"[green]:heavy_check_mark: {event.data}[/green]"
                        )
                    case FetcherEvent.Type.EXCEPTION:
                        self.progress.log(f"[red]{event.data}[/red]")

                tasks[idx] = asyncio.create_task(fetchers[idx].__anext__())
