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
            # --- Generate all combinations ---
            step_names = list(steps.keys())
            strategy_lists = [steps[name] for name in step_names]
            experiment_combinations = list(product(*strategy_lists))

            main_idx = starting_step_number + 1

            main_task_id = progress.add_task(
                f"{main_idx}. EXPERIMENTS", total=len(experiment_combinations)
            )

            experiments: list[tuple[int, IMultiStep]] = []
            for exp_idx, combination in enumerate(experiment_combinations, 1):
                step_dict = {
                    step_names[i]: [strategy] for i, strategy in enumerate(combination)
                }

                step_instance = inject(
                    IMultiStep,
                    "experiments",
                    progress=progress,
                    task_id=exp_idx,
                    step=step_dict,
                )
                experiments.append((exp_idx, step_instance))

            async def runner():
                for exp_idx, step in experiments:
                    strat_task_ids = []
                    for strat_idx, strat in enumerate(step.step):
                        numbering = f"{main_idx}.{exp_idx}.{strat_idx + 1}"
                        description = f"{numbering} {step.get_steps()[strat_idx].description}"
                        task_id = progress.add_task(description, total=step.calculate_total())
                        strat_task_ids.append(task_id)

                    run = await step.get_tasks(cache)

                    async def consume_gen(gen, task_id):
                        async for event in gen:
                            step.log(event)
                        progress.advance(task_id)

                    async def run_task(task: Task, gens, task_id):
                        await asyncio.gather(*(consume_gen(gen, task_id) for gen in gens))
                        step.log(task.completed_callback())

                    # Run all strategy tasks in this experiment
                    for i, (task, gens) in enumerate(run.items()):
                        await asyncio.gather(run_task(task, gens, strat_task_ids[i]))

                    # Mark experiment complete
                    progress.advance(main_task_id)

            # --- Run all experiments in a single event loop ---
            asyncio.run(runner())

            return len(experiment_combinations)
