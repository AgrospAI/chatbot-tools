from typing import Generator, Iterable, override

from rich.console import Console

from fastrag.config.config import Source, Step
from fastrag.fetchers.fetcher import Fetcher
from fastrag.steps.steps import StepRunner

console = Console()


class SourceStep(StepRunner):

    def __init__(self, step: Step) -> None:
        self._step: list[Source] = step

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["sources"]

    @override
    def run_step(self) -> Generator[None, None, None]:
        for source in self._step:
            strategy = source["strategy"]
            params = source["params"]

            print(params)

            fetcher: Fetcher = Fetcher.get_supported_instance(strategy)(**params)
            fetcher.fetch()
            yield
