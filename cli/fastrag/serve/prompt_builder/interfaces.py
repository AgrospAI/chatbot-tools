from abc import ABC, abstractmethod
from typing import Sequence

from pydantic import BaseModel


class Context(BaseModel):
    sources: Sequence[str]
    prompt: str


class IPromptBuilder(ABC):
    @abstractmethod
    def build_prompt(
        self,
        context: str,
        question: str,
    ) -> str:
        """Build the final prompt with the context and question.

        Args:
            context (str): prompt context
            question (str): user question

        Returns:
            str: prompt
        """

    @abstractmethod
    async def get_context(
        self,
        question: str,
    ) -> Context:
        """Build the full question with context.

        Args:
            question (str): question asked

        Returns:
            Context: Full context to add to the prompt
        """
