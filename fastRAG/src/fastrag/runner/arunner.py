import asyncio
from dataclasses import dataclass
from typing import get_args, override

from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from fastrag import Config
from fastrag.config.config import StepNames
from fastrag.plugins import PluginRegistry, plugin
from fastrag.runner.runner import IRunner
from fastrag.steps.step import IStep
from fastrag.systems import System


@dataclass(frozen=True)
@plugin(system=System.RUNNER)
class Runner(IRunner):

    def calculate_total(self) -> int:
        return len(self.step)

    @override
    def run(self, config: Config, run_steps: int) -> None:
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
            names = [
                step for step in get_args(StepNames) if getattr(config.steps, step)
            ]

            runners: dict[str, IStep] = {
                step: PluginRegistry.get_instance(
                    System.STEP,
                    step,
                    progress=progress,
                    task_id=idx,
                    step=getattr(config.steps, step),
                )
                for idx, step in enumerate(names)
            }

            for step_idx, step in enumerate(names):
                progress.add_task(
                    f"{step_idx + 1}. {runners[step].description} -",
                    total=runners[step].calculate_total(),
                )

                async def runner_loop(step: IStep):
                    if step is None or not step.is_present:
                        return

                    runners = step.get_tasks()
                    tasks = [asyncio.create_task(run.__anext__()) for run in runners]

                    while tasks:
                        done, _ = await asyncio.wait(
                            tasks,
                            return_when=asyncio.FIRST_COMPLETED,
                        )

                        for d in done:
                            idx = tasks.index(d)

                            try:
                                event = d.result()
                            except StopAsyncIteration:
                                tasks.pop(idx)
                                runners.pop(idx)
                                progress.advance(step.task_id)
                                continue

                            step.callback(event)
                            tasks[idx] = asyncio.create_task(runners[idx].__anext__())

                asyncio.run(runner_loop(runners[step]))

                # Manual stop of application after given step
                if run_steps == step_idx + 1:
                    progress.print(
                        Panel.fit(
                            f"Stopping execution after step [bold yellow]{step.capitalize()}[/bold yellow]",
                            border_style="red",
                        ),
                        justify="center",
                    )
                    progress.stop()
                    break
