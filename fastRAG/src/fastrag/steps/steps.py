from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import get_args

from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from fastrag import Config, IPluginFactory
from fastrag.config.config import StepNames
from fastrag.events import Event
from fastrag.steps.logs import LogCallback, set_logging_callback


@dataclass(frozen=True)
class IStepRunner(IPluginFactory, ABC):

    progress: Progress
    task_id: int
    _callback: LogCallback = field(init=False, repr=False)

    def __post_init__(self) -> None:
        set_logging_callback(self)

    @abstractmethod
    def _log(self, event: Event) -> None: ...

    @abstractmethod
    def _log_verbose(self, event: Event) -> None: ...

    def calculate_total(self) -> int:
        return len(self.step)

    @classmethod
    def run(cls, config: Config, up_to: str) -> None:
        with Progress(
            TextColumn(
                "[progress.percentage]{task.description} {task.percentage:>3.0f}%"
            ),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
        ) as progress:
            names = get_args(StepNames)
            runners: dict[str, IStepRunner] = {
                step: IStepRunner.get_supported_instance(step)(
                    progress=progress,
                    task_id=idx,
                    step=getattr(config.steps, step),
                )
                for idx, step in enumerate(names)
            }

            for step_idx, step in enumerate(names):
                progress.add_task(
                    f"{step_idx + 1}. {runners[step].description} -",
                    total=runners[step].calculate_total(),
                )

                runner = runners[step]
                runner.run()

                # Manual stop of application after given step
                if up_to == step_idx + 1:
                    progress.print(
                        Panel.fit(
                            f"Stopping execution after step [bold yellow]{step.capitalize()}[/bold yellow]",
                            border_style="red",
                        ),
                        justify="center",
                    )
                    progress.stop()
                    break
