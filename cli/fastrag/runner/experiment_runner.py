import asyncio
from dataclasses import dataclass, field
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

from fastrag.cache.cache import ICache
from fastrag.config.config import Steps
from fastrag.plugins import inject
from fastrag.runner.runner import IRunner
from fastrag.steps.step import IMultiStep


@dataclass(frozen=True)
class ExperimentsRunner(IRunner):
    supported: ClassVar[str] = "async_experiments"

    max_concurrent: int = field(default=5)

    @override
    def run(
        self,
        steps: Steps,
        cache: ICache,
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
            step_names = list(steps.keys())
            strategy_lists = [steps[name] for name in step_names]
            experiment_combinations = list(product(*strategy_lists))

            main_idx = starting_step_number + 1

            experiments_task_id = progress.add_task(
                f"{main_idx}. EXPERIMENTS",
                total=len(experiment_combinations),
            )

            experiments: list[IMultiStep] = []

            for exp_idx, combination in enumerate(experiment_combinations, start=1):
                step_dict = {
                    step_names[i]: [strategy] for i, strategy in enumerate(combination)
                }

                step_instance: IMultiStep = inject(
                    IMultiStep,
                    "experiments",
                    progress=progress,
                    task_id=exp_idx,
                    step=step_dict,
                )

                experiments.append(step_instance)

            semaphore = asyncio.Semaphore(self.max_concurrent) if self.max_concurrent else None

            async def run_single_experiment(exp_idx: int, experiment: IMultiStep):
                if semaphore:
                    async with semaphore:
                        await _run_experiment(exp_idx, experiment)
                else:
                    await _run_experiment(exp_idx, experiment)

            async def _run_experiment(exp_idx: int, experiment: IMultiStep):
                async for task, generators in experiment.get_tasks(cache):
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

            return len(experiment_combinations)
