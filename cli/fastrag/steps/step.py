from __future__ import annotations

import base64
import random
import string
import uuid
from abc import ABC, abstractmethod
from dataclasses import InitVar, dataclass, field
from typing import TYPE_CHECKING, AsyncGenerator, ClassVar, TypeAlias, override

from rich.progress import Progress

from fastrag.cache.cache import ICache
from fastrag.cache.filters import MetadataFilter
from fastrag.config.config import Step, Steps
from fastrag.events import Event
from fastrag.helpers.filters import Filter
from fastrag.llms.llm import ILLM
from fastrag.plugins import PluginBase, inject
from fastrag.steps.logs import Loggable
from fastrag.stores.store import IVectorStore

if TYPE_CHECKING:
    from fastrag.runner.experiment_runner import Experiment
    from fastrag.steps.task import Task


@dataclass(frozen=True)
class RuntimeResources:
    cache: ICache
    store: IVectorStore
    llm: ILLM


Tasks: TypeAlias = AsyncGenerator[tuple["Task", list[AsyncGenerator[Event, None]]], None]


@dataclass
class IStep(Loggable, PluginBase, ABC):
    description: ClassVar[str] = "UNKNOWN STEP"

    filter: Filter | None = field(init=False, repr=False, hash=False, compare=False)

    task_id: int = field(default=-1)
    step: Step = field(default_factory=list)
    progress: Progress = field(default=None, compare=False, repr=False)
    resources: RuntimeResources = field(default=None, compare=False, repr=False)

    _tasks: list[Task] = field(init=False, default_factory=list, hash=False, repr=False)

    experiment: InitVar[Experiment | None] = None

    def __post_init__(self, experiment: Experiment) -> None:
        super().__post_init__()

        from fastrag.steps.task import Task

        self._tasks = [
            inject(
                Task,
                s.strategy,
                experiment=experiment,
                resources=self.resources,
                **s.params or {},
            )
            for s in self.step
        ]

    @property
    def cache(self) -> ICache:
        return self.resources.cache

    def calculate_total(self) -> int:
        """Calculates the number of tasks to perform by this step

        Returns:
            int: number of tasks to perform
        """
        return len(self.step) if self.step else 0

    @override
    def log_verbose(self, event: Event) -> None:
        match event.type:
            case Event.Type.PROGRESS:
                self.progress.log(event.data)
            case Event.Type.COMPLETED:
                self.progress.log(f"[green]:heavy_check_mark: {event.data}[/green]")
            case Event.Type.EXCEPTION:
                self.progress.log(f"[red]:x: {event.data}[/red]")
            case _:
                self.progress.log(f"[red]:?: UNEXPECTED EVENT: {event}[/red]")

    @override
    def log_normal(self, event: Event) -> None:
        match event.type:
            case Event.Type.PROGRESS:
                ...
            case _:
                self.log_verbose(event)

    @abstractmethod
    async def get_tasks(self) -> Tasks:
        """Generate a dict with the tasks to perform

        Returns:
            Tasks: dict with Task instance - Async generator of callbacks
        """

        raise NotImplementedError


ALPHANUM_UNDERSCORE = string.ascii_letters + string.digits + "_"


def generate_alphanum_id(experiment: IMultiStep, length: int = 22) -> str:
    # Deterministic path
    if experiment is not None:
        # Serialize and to bytes the experiment steps as seed

        rng = random.Random(repr(experiment).encode("utf-8"))
        return "".join(rng.choice(ALPHANUM_UNDERSCORE) for _ in range(length))

    # Non-deterministic path (UUID-based)
    raw = uuid.uuid4().bytes
    encoded = base64.urlsafe_b64encode(raw).decode("ascii")
    return encoded.rstrip("=").replace("-", "_")[:length]


@dataclass
class IMultiStep(IStep):
    experiment: InitVar[any] = None

    experiment_hash: str = field(init=False, default="")
    step: Steps = field(default_factory=dict, repr=False)
    results: str = field(default="", repr=False)
    _tasks: list[IStep] = field(default_factory=list, init=False, hash=False, repr=False)

    def __post_init__(self, experiment: Experiment | None = None) -> None:
        super(IStep, self).__post_init__()

        experiment = experiment if experiment else self

        self._tasks = [
            inject(
                IStep,
                strat,
                experiment=self,
                task_id=idx,
                progress=self.progress,
                step=step,
                resources=self.resources,
            )
            for idx, (strat, step) in enumerate(self.step.items())
        ]

        self.experiment_hash = generate_alphanum_id(experiment)

        for task in self._tasks:
            task.filter = MetadataFilter(experiment=experiment.experiment_hash)

        lines = []
        for task in self._tasks:
            task_name = task.__class__.__name__
            lines.append(f"\t{task_name}:")

            for strat in task.step:
                lines.append(f"\t└─ {strat.strategy}")

        self.results = (
            f"Experiment #{self.task_id + 1} | {self.experiment_hash} :\n{'\n'.join(lines)}"
        )

    def tasks(self, step: str) -> list[Task]:
        tasks = []
        for task in self._tasks:
            if step not in task.supported:
                continue
            tasks.extend(task._tasks)
        return tasks

    def save_results(self, results: str) -> None:
        self.results += results
