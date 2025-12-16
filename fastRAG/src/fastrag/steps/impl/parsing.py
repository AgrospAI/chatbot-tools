from dataclasses import dataclass
from typing import AsyncIterable, ClassVar, Iterable, Mapping, override

from fastrag.config.config import Parsing
from fastrag.parsing.parser import IParser, ParsingEvent
from fastrag.steps.impl.arunner import IAsyncStepRunner


@dataclass(frozen=True)
class ParsingStep(IAsyncStepRunner):

    step: list[Parsing]
    description: ClassVar[str] = "Parsing fetched documents"

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["parsing"]

    @override
    def get_tasks(self) -> Mapping[int, AsyncIterable]:
        return [
            IParser.get_supported_instance(source.strategy)(source.use).parse()
            for source in self.step
        ]

    @override
    def callback(self, event: ParsingEvent) -> None:
        match event.type:
            case ParsingEvent.Type.PROGRESS:
                self.progress.log(event.data)
            case ParsingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case ParsingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]{event.data}[/red]")
