from typing import Generator, Iterable, override

from fastrag.steps.steps import StepRunner


class SourceStep(StepRunner):

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["sources"]

    @override
    def get_tasks(self) -> Iterable[str]:
        return [""]

    @override
    def run_step(self) -> Generator[int, None, None]:
        for step in self._step:
            yield 1
