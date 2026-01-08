from abc import ABC, abstractmethod
from typing import AsyncGenerator


class ILLM(ABC):
    """Abstract interface for Large Language Models"""

    @abstractmethod
    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """Stream LLM responses token by token.

        Args:
            prompt: The prompt to send to the LLM

        Yields:
            Token strings from the LLM response
        """
        pass

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate a complete response from the LLM.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            The complete response string
        """
        pass
