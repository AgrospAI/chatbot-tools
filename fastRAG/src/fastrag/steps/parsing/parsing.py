from abc import ABC, abstractmethod
from typing import AsyncGenerator

from fastrag.steps.parsing.events import ParsingEvent


class IParser(ABC):
    """Base abstract class that represents data fetchers"""

    @abstractmethod
    async def parse(self) -> AsyncGenerator[ParsingEvent, None]:
        """Parses a file to markdown format

        Yields:
            ParsingEvent:
        """

        raise NotImplementedError
