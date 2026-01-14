from abc import ABC, abstractmethod

from fastrag.config.config import Steps
from fastrag.plugins import PluginBase
from fastrag.steps.step import RuntimeResources


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
