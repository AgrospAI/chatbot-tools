import asyncio
from dataclasses import InitVar, dataclass, field
from itertools import product
from typing import ClassVar, override

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from fastrag.config.config import Steps
from fastrag.helpers.experiments import Experiments
from fastrag.plugins import inject
from fastrag.runner.runner import IRunner
from fastrag.steps.step import IMultiStep, RuntimeResources


@dataclass(frozen=True)
class ExperimentsRunner(IRunner):
    supported: ClassVar[str] = "async_experiments"

    max_concurrent: InitVar[int] = field(default=5)

    _benchmarking_steps: Steps | None = field(default=None, init=False, repr=False)
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
        with Progress(
            TextColumn("[progress.percentage]{task.description} {task.percentage:>3.0f}%"),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
        ) as progress:
            is_benchmarking = "benchmarking" in steps.keys()
            if is_benchmarking:
                benchmarking = steps.pop("benchmarking")
                object.__setattr__(self, "_benchmarking_steps", benchmarking)

            step_names = list(steps.keys())
            strategy_lists = [steps[name] for name in step_names]
            experiment_combinations = list(product(*strategy_lists))

            main_idx = starting_step_number + 1

            experiments_task_id = progress.add_task(
                f"{main_idx}. EXPERIMENTS",
                total=len(experiment_combinations),
            )

            experiments: Experiments = []
            for idx, combination in enumerate(experiment_combinations):
                step_dict = {
                    step_names[i]: [strategy] for i, strategy in enumerate(combination)
                }
                step_dict["benchmarking"] = benchmarking
                experiments.append(
                    inject(
                        IMultiStep,
                        "experiments",
                        task_id=idx,
                        progress=progress,
                        step=step_dict,
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
