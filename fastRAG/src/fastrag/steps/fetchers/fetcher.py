from abc import ABC, abstractmethod
from typing import AsyncGenerator

from fastrag.steps.fetchers.events import FetchingEvent


class IFetcher(ABC):
    """Base abstract class that represents data fetchers"""

    @abstractmethod
    async def fetch(self) -> AsyncGenerator[FetchingEvent, None]:
        """Fetches a data source

        Yields:
            FetchingEvent:
        """

        raise NotImplementedError
