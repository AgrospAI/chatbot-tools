import asyncio
from dataclasses import dataclass
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
from fastrag.steps.task import Task


@dataclass(frozen=True)
class ExperimentsRunner(IRunner):
    supported: ClassVar[str] = "async_experiments"

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
            # ------------------------------------------------------------
            # Generate experiment combinations
            # ------------------------------------------------------------
            step_names = list(steps.keys())
            strategy_lists = [steps[name] for name in step_names]
            experiment_combinations = list(product(*strategy_lists))

            main_idx = starting_step_number + 1

            experiments_task_id = progress.add_task(
                f"{main_idx}. EXPERIMENTS",
                total=len(experiment_combinations),
            )

            # ------------------------------------------------------------
            # Build IMultiStep instances
            # ------------------------------------------------------------
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

            # ------------------------------------------------------------
            # Async runner
            # ------------------------------------------------------------
            async def run_all():
                for exp_idx, experiment in enumerate(experiments, start=1):
                    # Each IMultiStep yields tasks lazily, already ordered
                    async for task, generators in experiment.get_tasks(cache):
                        # Each yielded task corresponds to a *single concrete step*
                        step_description = task.supported

                        if isinstance(step_description, list):
                            step_description = step_description[0].upper()
                        else:
                            step_description = step_description.upper()

                        task_id = progress.add_task(
                            f"{main_idx}.{exp_idx} {step_description}",
                            total=len(generators),
                        )

                        async def consume(gen):
                            async for event in gen:
                                experiment.log(event)
                            progress.advance(task_id)

                        await asyncio.gather(*(consume(gen) for gen in generators))
                        experiment.log(task.completed_callback())

                    # Mark experiment completed
                    progress.advance(experiments_task_id)

            asyncio.run(run_all())

            return len(experiment_combinations)
