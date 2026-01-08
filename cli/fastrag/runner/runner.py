from abc import ABC, abstractmethod

from fastrag.config.config import Config


class IRunner(ABC):
    """Base abstract class for running the configuration file"""

    @abstractmethod
    def run(self, config: Config, run_steps: int) -> None: ...
