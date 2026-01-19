from abc import ABC, abstractmethod
from dataclasses import InitVar, dataclass, field

from rich.progress import Progress

from fastrag.config.config import Resources
from fastrag.helpers.experiments import Experiment
from fastrag.plugins import PluginBase, inject
from fastrag.steps.logs import Loggable


@dataclass
class IStepCommon(PluginBase, ABC):
    progress: InitVar[Progress] = field()

    task_id: int
    resources: Resources = field(repr=False)

    experiment: Experiment | None = field(init=False, repr=False)
    logger: Loggable = field(init=False, repr=False)

    def __post_init__(self, progress: Progress, *args, **kwargs) -> None:
        self.logger = inject(Loggable, "rich", progress=progress)

    @abstractmethod
    def calculate_total(self) -> int:
        """Calculates the number of tasks to perform by this step

        Returns:
            int: number of tasks to perform
        """

        raise NotImplementedError
