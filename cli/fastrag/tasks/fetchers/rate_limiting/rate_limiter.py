from abc import abstractmethod
from dataclasses import dataclass

from fastrag.plugins import PluginBase


@dataclass(frozen=True)
class IRateLimiter(PluginBase):
    delay: float = 1.0  # seconds between requests

    @abstractmethod
    async def wait(self, uri: str):
        """Needed wait for given URI

        Args:
            uri (str): URI to check
        """
        raise NotImplementedError
