from typing import Generator, Iterable, override

from fastrag.steps.steps import StepRunner


class ChunkingStep(StepRunner):

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["chunking"]

    @override
    def run_step(self) -> Generator[None, None, None]:
        for step in self._step:
            yield 1
