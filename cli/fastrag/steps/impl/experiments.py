from dataclasses import dataclass
from typing import AsyncGenerator, ClassVar, override

from fastrag.cache.cache import ICache
from fastrag.events import Event
from fastrag.plugins import inject
from fastrag.steps.step import IMultiStep, IStep
from fastrag.steps.task import Task


@dataclass
class ExperimentsStep(IMultiStep):
    supported: ClassVar[str] = "experiments"
    description: ClassVar[str] = "EXPERIMENTS"

    @override
    def get_steps(self) -> list[IStep]:
        return [
            inject(
                IStep,
                strat,
                progress=self.progress,
                task_id=self.task_id,
                step=step,
            )
            for strat, step in self.step.items()
        ]

    @override
    async def get_tasks(self, cache: ICache) -> dict[Task, list[AsyncGenerator[Event, None]]]:
        tasks = {}

        for step in self.get_steps():
            step_tasks = await step.tasks(cache)
            # Merge steps
            tasks.update(step_tasks)

        return tasks
