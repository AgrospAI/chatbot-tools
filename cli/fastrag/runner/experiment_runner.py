import asyncio
from dataclasses import InitVar, dataclass, field
from itertools import product
from typing import ClassVar, override

from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from fastrag.config.models import Steps
from fastrag.helpers.experiments import Experiment
from fastrag.helpers.resources import RuntimeResources
from fastrag.plugins import inject
from fastrag.runner.runner import IRunner
from fastrag.steps.step import IStep
from fastrag.steps.step_group import IMultiStep
from fastrag.tasks.base import Task

console = Console()


@dataclass(frozen=True)
class ExperimentsRunner(IRunner):
    supported: ClassVar[str] = "async_experiments"

    max_concurrent: InitVar[int] = field(default=5)

    _semaphore: asyncio.Semaphore | None = field(default=None, init=False, repr=False)

    def __post_init__(self, max_concurrent: int) -> None:
        semaphore = asyncio.Semaphore(max_concurrent) if max_concurrent else None
        object.__setattr__(self, "_semaphore", semaphore)

    @override
    async def run(
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
                            experiment.logger.log(event)
                        progress.advance(step_task_id)

                    await asyncio.gather(*(consume(gen) for gen in generators))
                    experiment.logger.log(task.completed_callback())

                progress.advance(experiments_task_id)

            await asyncio.gather(
                *(
                    run_single_experiment(idx, exp)
                    for idx, exp in enumerate(experiments, start=1)
                )
            )

        for idx, experiment in enumerate(experiments, start=1):
            self.report_experiment(experiment, idx)

        self.report_summary(experiments)

        return len(experiment_combinations)

    def report_summary(self, experiments: list[Experiment]):
        combined_text = Text()

        for index, experiment in enumerate(experiments, start=1):
            header = Text()
            header.append(f"\nExperiment #{index} ", style="bold cyan")
            header.append(f"{experiment.hash} ", style="dim")
            header.append("Score ", style="bold")
            header.append(f"{experiment.score}", style="bold green")
            combined_text.append(header)

        console.print(
            Align.center(Panel(combined_text, title="Experiments Summary", expand=False))
        )

    def report_experiment(self, experiment: Experiment, index: int):
        # --- Build the tree ---
        tree = Tree("[bold]Pipeline[/bold]")
        for key, step in experiment.steps.items():
            s = tree.add(f"[bold]{key.capitalize()}[/bold]")
            s.add(step.tasks[0].get_supported_name())

        # --- Build the benchmarks table ---
        benchmarks = experiment.tasks("benchmarking")
        table = Table(title="Benchmark Scores", show_header=True, header_style="bold magenta")
        table.add_column("Metric")
        table.add_column("Value", justify="right")

        if benchmarks:
            for bench in benchmarks:
                table.add_row(bench.get_supported_name(), f"[green]{bench.results}[/green]")
        else:
            table.add_row("No benchmarks", "-")

        # --- Place tree and table side by side ---
        columns = Columns([tree, table], align="left", expand=False, equal=False)

        # --- Wrap everything in a full-width panel ---
        panel = Panel(
            columns,
            title=f"Experiment #{index} {experiment.hash}",
            expand=False,
            border_style="cyan",
        )

        console.print(Align.center(panel))
