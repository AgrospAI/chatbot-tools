from abc import ABC, abstractmethod

from fastrag.config.config import Config
from fastrag.plugins import PluginBase


class IRunner(PluginBase, ABC):
    """Base abstract class for running the configuration file"""

    @abstractmethod
    def run(self, config: Config, run_steps: int) -> None: ...
