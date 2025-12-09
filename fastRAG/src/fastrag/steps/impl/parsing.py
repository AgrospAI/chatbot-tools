from dataclasses import dataclass
from typing import Generator, Iterable, override

from fastrag.config.config import Parsing
from fastrag.steps.steps import StepRunner


@dataclass(frozen=True)
class ParsingStep(StepRunner):

    step: list[Parsing]

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["parsing"]

    @override
    def run_step(self) -> Generator[None, None, None]:
        for step in self.step:
            yield
