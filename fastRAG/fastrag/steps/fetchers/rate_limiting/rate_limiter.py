from abc import abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class RateLimiter:
    delay: float = 1.0  # seconds between requests

    @abstractmethod
    async def wait(self, uri: str):
        """Needed wait for given URI

        Args:
            uri (str): URI to check
        """
        raise NotImplementedError
