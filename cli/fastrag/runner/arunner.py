import asyncio
from dataclasses import dataclass
from typing import ClassVar, override

from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from fastrag.cache.cache import ICache
from fastrag.config.config import Steps
from fastrag.plugins import inject
from fastrag.runner.runner import IRunner
from fastrag.steps.step import IStep
from fastrag.steps.task import Task


@dataclass(frozen=True)
class Runner(IRunner):
    supported: ClassVar[str] = "async"

    @override
    def run(
        self,
        steps: Steps,
        cache: ICache,
        run_steps: int = -1,
        starting_step_number: int = 0,
    ) -> int:
        with Progress(
            TextColumn("[progress.percentage]{task.description} {task.percentage:>3.0f}%"),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
        ) as progress:
            steps = [
                inject(
                    IStep,
                    step,
                    progress=progress,
                    task_id=idx,
                    step=steps[step],
                )
                for idx, step in enumerate(steps)
            ]

            for step in steps:
                progress.add_task(
                    f"{step.task_id + starting_step_number + 1}. {step.description} -",
                    total=step.calculate_total(),
                )

                async def runner_loop(step: IStep):
                    run = await step.tasks(cache)

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

                asyncio.run(runner_loop(step))

                # Manual stop of application after given step
                if run_steps == step.task_id + 1:
                    progress.print(
                        Panel.fit(
                            f"Stopping execution after step "
                            f"[bold yellow]{step.capitalize()}[/bold yellow]",
                            border_style="red",
                        ),
                        justify="center",
                    )
                    progress.stop()
                    return run_steps

            return len(steps)
