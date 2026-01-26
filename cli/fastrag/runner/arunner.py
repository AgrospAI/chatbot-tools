import asyncio
from dataclasses import dataclass
from typing import ClassVar, override

from fastrag.config.models import Steps
from fastrag.helpers.resources import RuntimeResources
from fastrag.plugins import inject
from fastrag.runner.runner import IRunner
from fastrag.steps.step import IStep
from fastrag.tasks.base import Task


@dataclass(frozen=True)
class Runner(IRunner):
    supported: ClassVar[str] = "async"

    @override
    async def run(
        self,
        steps: Steps,
        resources: RuntimeResources,
        starting_step_number: int = 0,
    ) -> int:
        with self.progress_bar() as progress:
            instances: list[IStep] = []
            for idx, (step, tasks) in enumerate(steps.items()):
                tasks = [
                    inject(Task, t.strategy, resources=resources, **t.params or {})
                    for t in tasks
                ]

                instances.append(
                    inject(
                        IStep,
                        step,
                        tasks=tasks,
                        task_id=idx,
                        progress=progress,
                        resources=resources,
                    )
                )

            for step in instances:
                step_number = step.task_id + starting_step_number + 1

                # Step-level progress bar
                step_task_id = progress.add_task(
                    f"{step_number}. {step.description}",
                    total=step.calculate_total(),
                )

                async for task, generators in step.get_tasks():

                    async def consume(gen):
                        async for event in gen:
                            step.logger.log(event)

                    await asyncio.gather(*(consume(gen) for gen in generators))
                    step.logger.log(task.completed_callback())

                    progress.advance(step_task_id)

            return len(instances)
