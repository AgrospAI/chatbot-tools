import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from typing import Literal

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from fastrag import Cache, Config, PluginFactory

STEP_TYPE = Literal["sources", "parsing", "chunking", "embedding", "benchmarking"]
console = Console()


@dataclass(frozen=True)
class StepRunner(PluginFactory, ABC):

    progress: Progress
    task_id: int
    cache: Cache

    @abstractmethod
    async def run_step(self) -> None: ...

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

        with Progress(
            TextColumn(
                "[progress.percentage]{task.description} {task.percentage:>3.0f}%"
            ),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
        ) as progress:
            runners: dict[str, StepRunner] = {
                step.name: StepRunner.get_supported_instance(step.name)(
                    progress=progress,
                    task_id=idx,
                    cache=cache,
                    step=getattr(config.steps, step.name),
                )
                for idx, step in enumerate(steps)
            }

            for step_idx, step in enumerate(step_names):
                progress.add_task(
                    f"{step_idx + 1}. {descriptions[step]} -",
                    total=runners[step].calculate_total(),
                )

                runner = runners[step]

                async def runner_loop():
                    await runner.run_step()

                asyncio.run(runner_loop())

                # Manual stop of application after given step
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
