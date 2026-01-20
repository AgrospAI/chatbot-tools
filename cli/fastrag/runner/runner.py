from abc import ABC, abstractmethod

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from fastrag.config.config import Steps
from fastrag.helpers.resources import RuntimeResources
from fastrag.plugins import PluginBase


class IRunner(PluginBase, ABC):
    """Base abstract class for running the configuration file"""

    @abstractmethod
    def run(
        self,
        steps: Steps,
        resources: RuntimeResources,
        starting_step_number: int = 0,
    ) -> int:
        """Run the given steps, up to `run_steps`

        Args:
            steps (Steps): steps to run
            resources (RuntimeResources): resources to use such as cache, vectorstore ...
            starting_step_number (int, optional): Starting step number, for debugging.
            Defaults to 0.

        Returns:
            int: Number of ran steps
        """

        raise NotImplementedError

    def progress_bar(self) -> Progress:
        return Progress(
            TextColumn("[progress.percentage]{task.description} {task.percentage:>3.0f}%"),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
        )
