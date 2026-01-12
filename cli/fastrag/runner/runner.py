from abc import ABC, abstractmethod

from fastrag.cache.cache import ICache
from fastrag.config.config import Steps
from fastrag.plugins import PluginBase


class IRunner(PluginBase, ABC):
    """Base abstract class for running the configuration file"""

    @abstractmethod
    def run(
        self, steps: Steps, cache: ICache, run_steps: int = -1, starting_step_number: int = 0
    ) -> int:
        """Run the given steps, up to `run_steps`

        Args:
            steps (Steps): steps to run
            cache (ICache): cache to use
            run_steps (int, optional): Steps to run up to (-1 == all). Defaults to -1.
            starting_step_number (int, optional): Starting step number, for debugging.
            Defaults to 0.

        Returns:
            int: Number of ran steps
        """

        raise NotImplementedError
