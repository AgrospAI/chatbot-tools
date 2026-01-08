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

from fastrag.config.config import Config, StepNames
from fastrag.plugins import PluginRegistry, plugin
from fastrag.runner.runner import IRunner
from fastrag.steps.step import IStep
from fastrag.steps.task import Task
from fastrag.systems import System


@dataclass(frozen=True)
@plugin(system=System.RUNNER, supported="async")
class Runner(IRunner):
    @override
    def run(self, config: Config, run_steps: int) -> None:
        with Progress(
            TextColumn("[progress.percentage]{task.description} {task.percentage:>3.0f}%"),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
        ) as progress:
            names = [step for step in get_args(StepNames) if getattr(config.steps, step)]

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

                    run = await step.tasks()

                    async def consume_gen(gen):
                        async for event in gen:
                            step.log(event)

                    async def run_task(task: Task, gens):
                        tasks = [asyncio.create_task(consume_gen(gen)) for gen in gens]
                        await asyncio.gather(*tasks)
                        step.log(task.completed_callback())
                        progress.advance(task_id=step.task_id)

                    await asyncio.gather(
                        *(run_task(task, generators) for task, generators in run.items())
                    )

                asyncio.run(runner_loop(runners[step]))

                # Manual stop of application after given step
                if run_steps == step_idx + 1:
                    progress.print(
                        Panel.fit(
                            f"Stopping execution after step "
                            f"[bold yellow]{step.capitalize()}[/bold yellow]",
                            border_style="red",
                        ),
                        justify="center",
                    )
                    progress.stop()
                    break
