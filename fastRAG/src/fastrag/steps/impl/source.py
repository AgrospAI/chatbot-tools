from dataclasses import dataclass
from typing import AsyncIterable, ClassVar, Iterable, Mapping, override

from fastrag.config.config import Source
from fastrag.fetchers.fetcher import FetchingEvent, IFetcher
from fastrag.steps.impl.arunner import IAsyncStepRunner


@dataclass(frozen=True)
class SourceStep(IAsyncStepRunner):

    step: list[Source]
    description: ClassVar[str] = "Fetching sources"

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["sources"]

    @override
    def get_tasks(self) -> Mapping[int, AsyncIterable]:
        return [
            IFetcher.get_supported_instance(source.strategy)(**source.params).fetch()
            for source in self.step
        ]

    @override
    def callback(self, event: FetchingEvent) -> None:
        match event.type:
            case FetchingEvent.Type.PROGRESS:
                self.progress.log(event.data)
            case FetchingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case FetchingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]{event.data}[/red]")
