from abc import ABC, abstractmethod
from pathlib import Path

from fastrag.config.config import Config


class IConfigLoader(ABC):
    """Base abstract class for config loader plugins to extend"""

    @abstractmethod
    def load(self, config: Path) -> Config:
        """Loads a configuration object from the given file path.

        Args:
            config (Path): configuration file path

        Returns:
            Config: configuration instance
        """
        raise NotImplementedError
