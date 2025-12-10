from dataclasses import dataclass
from typing import Iterable, override

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
    async def run_step(self) -> None: ...
