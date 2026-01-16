import asyncio
from dataclasses import InitVar, dataclass, field
from itertools import product
from typing import ClassVar, override

from fastrag.config.config import Steps
from fastrag.helpers.experiments import Experiment
from fastrag.plugins import inject
from fastrag.runner.runner import IRunner
from fastrag.steps.resources import RuntimeResources
from fastrag.steps.step import IStep
from fastrag.steps.step_group import IMultiStep
from fastrag.steps.task import Task


@dataclass(frozen=True)
class ExperimentsRunner(IRunner):
    supported: ClassVar[str] = "async_experiments"

    max_concurrent: InitVar[int] = field(default=5)

    _semaphore: asyncio.Semaphore | None = field(default=None, init=False, repr=False)

    def __post_init__(self, max_concurrent: int) -> None:
        semaphore = asyncio.Semaphore(max_concurrent) if max_concurrent else None
        object.__setattr__(self, "_semaphore", semaphore)

    @override
    def run(
        self,
        steps: Steps,
        resources: RuntimeResources,
        starting_step_number: int = 0,
    ) -> int:
        with self.progress_bar() as progress:
            is_benchmarking = "benchmarking" in steps.keys()
            if is_benchmarking:
                benchmarking = steps.pop("benchmarking")

            step_names = list(steps.keys())
            strategy_lists = [steps[name] for name in step_names]
            experiment_combinations = list(product(*strategy_lists))

            main_idx = starting_step_number + 1

            experiments_task_id = progress.add_task(
                f"{main_idx}. EXPERIMENTS",
                total=len(experiment_combinations),
            )

            experiments: list[Experiment] = []

            for idx, strategies in enumerate(experiment_combinations):
                # From the different combinations of steps => Experiments
                step_dict = {}

                for step_idx, (name, strat) in enumerate(zip(step_names, strategies)):
                    task = inject(
                        Task,
                        strat.strategy,
                        resources=resources,
                        **strat.params or {},
                    )

                    step_dict[name] = inject(
                        IStep,
                        name,
                        task_id=step_idx,
                        tasks=[task],  # exactly ONE task
                        resources=resources,
                        progress=progress,
                    )

                if is_benchmarking:
                    tasks = [
                        inject(Task, s.strategy, resources=resources, **s.params or {})
                        for s in benchmarking
                    ]

                    step_dict["benchmarking"] = inject(
                        IStep,
                        "benchmarking",
                        task_id=len(step_names),
                        tasks=tasks,
                        resources=resources,
                        progress=progress,
                    )

                experiments.append(
                    inject(
                        IMultiStep,
                        "experiments",
                        task_id=idx,
                        progress=progress,
                        steps=step_dict,
                        resources=resources,
                    )
                )

            async def run_single_experiment(exp_idx: int, experiment: IMultiStep):
                if self._semaphore:
                    async with self._semaphore:
                        await _run_experiment(exp_idx, experiment)
                else:
                    await _run_experiment(exp_idx, experiment)

            async def _run_experiment(exp_idx: int, experiment: IMultiStep):
                async for task, generators in experiment.get_tasks():
                    task_name = task.supported
                    if isinstance(task_name, list):
                        task_name = task_name[0]

                    step_task_id = progress.add_task(
                        f"{main_idx}.{exp_idx} {task_name.upper()}",
                        total=len(generators),
                    )

                    async def consume(gen):
                        async for event in gen:
                            experiment.log(event)
                        progress.advance(step_task_id)

                    await asyncio.gather(*(consume(gen) for gen in generators))
                    experiment.log(task.completed_callback())

                progress.advance(experiments_task_id)

            async def run_all():
                await asyncio.gather(
                    *(
                        run_single_experiment(idx, exp)
                        for idx, exp in enumerate(experiments, start=1)
                    )
                )

            asyncio.run(run_all())

            for experiment in experiments:
                print(experiment.results)

            return len(experiment_combinations)
