from abc import ABC, abstractmethod
from dataclasses import field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastrag.steps.task import Task


class Experiment(ABC):
    hash: str = field(init=False, repr=False)

    @abstractmethod
    def tasks(self, step: str) -> list["Task"]:
        """Get the Task instance for the given step

        Args:
            step (str): step to look for

        Returns:
            list[Task]: list of Tasks of the given step
        """

        raise NotImplementedError
