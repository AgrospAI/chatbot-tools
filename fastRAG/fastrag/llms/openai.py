from dataclasses import dataclass
from typing import AsyncGenerator, override

from fastrag.llms.llm import ILLM
from fastrag.plugins import plugin
from fastrag.systems import System


@dataclass
@plugin(system=System.LLM, supported="openai")
class OpenAILLM(ILLM):
    """OpenAI-compatible LLM implementation"""

    api_key: str
    base_url: str
    model_name: str
    temperature: float = 0.0

    def __post_init__(self):
        """Initialize OpenAI client lazily"""
        self._llm = None

    def _get_llm(self):
        """Lazy initialization of OpenAI client"""
        if self._llm is None:
            try:
                from langchain_openai import ChatOpenAI
            except ImportError:
                raise ImportError(
                    "langchain-openai is required for OpenAI support. "
                    "Install it with: pip install langchain-openai"
                )

            self._llm = ChatOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                model_name=self.model_name,
                temperature=self.temperature,
                streaming=True,
            )

        return self._llm

    @override
    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """Stream responses from OpenAI"""
        llm = self._get_llm()

        async for chunk in llm.astream(prompt):
            if chunk.content:
                yield chunk.content

    @override
    async def generate(self, prompt: str) -> str:
        """Generate a complete response from OpenAI"""
        llm = self._get_llm()

        response = await llm.ainvoke(prompt)
        return response.content
