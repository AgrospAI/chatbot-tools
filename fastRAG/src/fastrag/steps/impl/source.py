from dataclasses import dataclass
from typing import Generator, Iterable, override

from rich.console import Console

from fastrag.config.config import Source
from fastrag.fetchers.fetcher import Fetcher
from fastrag.steps.steps import StepRunner

console = Console()


@dataclass(frozen=True)
class SourceStep(StepRunner):

    step: list[Source]

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["sources"]

    @override
    def run_step(self) -> Generator[None, None, None]:
        for source in self.step:
            Fetcher.get_supported_instance(source.strategy)(
                **source.params,
                cache=self.cache,
            ).fetch()

            yield
