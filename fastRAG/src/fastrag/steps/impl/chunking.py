from dataclasses import dataclass
from typing import ClassVar, Generator, Iterable, override

from fastrag.config.config import Chunking
from fastrag.events import Event
from fastrag.parsing.parser import ParsingEvent
from fastrag.steps.steps import IStepRunner


@dataclass(frozen=True)
class ChunkingStep(IStepRunner):

    step: list[Chunking]
    description: ClassVar[str] = "Chunking fetched documents"

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["chunking"]

    @override
    def run(self) -> Generator[ParsingEvent, None, None]: ...

    @override
    def callback(self, event: Event) -> None: ...
