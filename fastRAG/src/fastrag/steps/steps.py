from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
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
        cache, steps = config.cache, fields(config.steps)

        step_names: list[STEP_TYPE] = [f.name for f in steps]
        descriptions: dict[STEP_TYPE, str] = {
            "sources": "Fetching sources",
            "parsing": "Parsing fetched documents",
            "chunking": "Chunking fetched documents",
            "embedding": "Embedding chunks",
            "benchmarking": "Running benchmarks",
        }

        with Progress() as progress:
            runners: dict[str, StepRunner] = {
                step.name: StepRunner.get_supported_instance(step.name)(
                    cache=cache,
                    step=getattr(config.steps, step.name),
                )
                for step in steps
            }

            tasks = {
                step: progress.add_task(
                    f"{i}. {descriptions[step]}...",
                    total=runners[step].calculate_total(),
                )
                for i, step in enumerate(step_names, start=1)
            }

            for step_idx, step in enumerate(step_names):
                name, runner = step_names[step_idx], runners[step]

                for _ in runner.run_step():
                    progress.advance(tasks[name])

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
