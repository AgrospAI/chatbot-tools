from dataclasses import dataclass
from typing import ClassVar, Generator, Iterable, override

from fastrag.chunking.chunker import ChunkingEvent
from fastrag.config.config import Chunking
from fastrag.parsing.parser import ParsingEvent
from fastrag.steps.steps import IStepRunner


@dataclass(frozen=True)
class ChunkingStep(IStepRunner):

    step: list[Chunking]
    description: ClassVar[str] = "CHUNK"

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["chunking"]

    @override
    def run(self) -> Generator[ParsingEvent, None, None]: ...

    @override
    def _log_verbose(self, event: ChunkingEvent) -> None:
        match event.type:
            case ChunkingEvent.Type.PROGRESS:
                self.progress.log(event.data)
            case ChunkingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case ChunkingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")

    @override
    def _log(self, event: ChunkingEvent) -> None:
        match event.type:
            case ChunkingEvent.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case ChunkingEvent.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
