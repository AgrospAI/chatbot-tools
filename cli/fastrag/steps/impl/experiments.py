from dataclasses import dataclass, field
from itertools import product
from typing import AsyncGenerator, ClassVar, Dict, override

from fastrag.cache.cache import ICache
from fastrag.config.config import Steps, Strategy
from fastrag.events import Event
from fastrag.plugins import inject
from fastrag.steps.step import IStep
from fastrag.steps.task import Task


@dataclass
class ExperimentsStep(IStep):
    description: ClassVar[str] = "EMBED"
    supported: ClassVar[str] = "embedding"

    step: Steps
    _combinations: list[list[Strategy]] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        step_names = list(self.step.keys())
        step_strategy_lists = [self.step[name] for name in step_names]

        # Cartesian product of all step strategies
        self._combinations = [list(combo) for combo in product(*step_strategy_lists)]
        print(self._combinations)

    @override
    async def get_tasks(self, cache: ICache) -> Dict[Task, AsyncGenerator[Event, None]]:
        tasks = {}
        for combination in self._combinations:
            for strat in combination:
                instance: Task = inject(Task, strat.strategy, cache=cache, **strat.params)
                entries = await cache.get_entries(instance.filter)
                tasks[instance] = [instance.callback(uri, entry) for uri, entry in entries]

        return tasks
