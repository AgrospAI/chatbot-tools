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

from fastrag.config.config import Steps
from fastrag.plugins import inject
from fastrag.runner.runner import IRunner
from fastrag.steps.step import IStep, RuntimeResources


@dataclass(frozen=True)
class Runner(IRunner):
    supported: ClassVar[str] = "async"

    @override
    def run(
        self,
        steps: Steps,
        resources: RuntimeResources,
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
                    task_id=idx,
                    progress=progress,
                    step=steps[step],
                    resources=resources,
                )
                for idx, step in enumerate(steps)
            ]

            async def run_all():
                for step in steps:
                    step_number = step.task_id + starting_step_number + 1

                    # Step-level progress bar
                    step_task_id = progress.add_task(
                        f"{step_number}. {step.description}",
                        total=step.calculate_total(),
                    )

                    async for task, generators in step.get_tasks():

                        async def consume(gen):
                            async for event in gen:
                                step.log(event)

                        await asyncio.gather(*(consume(gen) for gen in generators))
                        step.log(task.completed_callback())

                        progress.advance(step_task_id)

                    # Manual stop support
                    if run_steps == step.task_id + 1:
                        progress.print(
                            Panel.fit(
                                f"Stopping execution after step "
                                f"[bold yellow]{step.description}[/bold yellow]",
                                border_style="red",
                            ),
                            justify="center",
                        )
                        return

            asyncio.run(run_all())
            return len(steps)
