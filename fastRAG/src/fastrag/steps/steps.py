from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generator, Literal

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

from fastrag import Cache, Config, PluginFactory

STEP_TYPE = Literal["sources", "parsing", "chunking", "embedding", "benchmarking"]
console = Console()


@dataclass(frozen=True)
class StepRunner(PluginFactory, ABC):

    cache: Cache

    @abstractmethod
    def run_step(self) -> Generator[None, None, None]: ...

    def calculate_total(self) -> int:
        return len(self.step)

    @classmethod
    def run(cls, config: Config, up_to: str) -> None:
        step_names: list[STEP_TYPE] = [
            "sources",
            "parsing",
            "chunking",
            "embedding",
            "benchmarking",
        ]
        descriptions: dict[STEP_TYPE, str] = {
            "sources": "Fetching sources",
            "parsing": "Parsing fetched documents",
            "chunking": "Chunking fetched documents",
            "embedding": "Embedding chunks",
            "benchmarking": "Running benchmarks",
        }

        cache, steps = config.cache, config.steps

        with Progress() as progress:
            runners: dict[str, StepRunner] = {
                step: StepRunner.get_supported_instance(step)(
                    cache=cache, step=steps[step_cfg]
                )
                for step, step_cfg in zip(step_names, steps)
            }

            tasks = {
                step: progress.add_task(
                    f"{i}. {descriptions[step]}...",
                    total=runners[step].calculate_total(),
                )
                for i, step in enumerate(step_names, start=1)
            }

            for step_idx, step in enumerate(steps):
                name, runner = step_names[step_idx], runners[step]

                for _ in runner.run_step():
                    progress.advance(tasks[name], advance=1)

                if up_to == step_idx + 1:
                    progress.stop()
                    console.print(
                        Panel.fit(
                            f"Stopping execution after step [bold yellow]'{step_names[step_idx]}'[/bold yellow]",
                            border_style="red",
                        ),
                        justify="center",
                    )
                    break
