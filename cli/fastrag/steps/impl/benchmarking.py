from dataclasses import dataclass
from typing import ClassVar, override

from fastrag.events import Event
from fastrag.steps.base import Tasks
from fastrag.steps.step import IStep


@dataclass
class BenchmarkingStep(IStep):
    supported: ClassVar[str] = "benchmarking"
    description: ClassVar[str] = "BENCH"

    @override
    async def get_tasks(self) -> Tasks:
        for task in self.tasks:
            yield (task, [task.run()])

        score = round(sum(task.results for task in self.tasks) / len(self.tasks), 3)
        self.experiment.score = score
        self.logger.log(
            Event(Event.Type.COMPLETED, f"Experiment {self.experiment.hash} score: {score}")
        )
