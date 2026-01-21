from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastrag.steps.step import IStep
    from fastrag.tasks.base import Task


@dataclass
class Experiment(ABC):
    steps: dict[str, "IStep"]
    hash: str = field(init=False, repr=False)

    score: float = field(init=False, repr=False)
    _results: str = field(init=False, repr=False)

    @abstractmethod
    def tasks(self, step: str) -> list["Task"]:
        """Get the Task instance for the given step

        Args:
            step (str): step to look for

        Returns:
            list[Task]: list of Tasks of the given step
        """

        raise NotImplementedError

    @abstractmethod
    def save_results(self, results: str) -> None:
        """Save trivial string to print

        Args:
            results (str): results
        """

        raise NotImplementedError
