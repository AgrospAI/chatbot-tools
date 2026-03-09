from dataclasses import InitVar, dataclass, field
from typing import AsyncGenerator, ClassVar, override

from langchain_openai import ChatOpenAI

from fastrag.llms.llm import ILLM


@dataclass
class OpenAILLM(ILLM):
    """OpenAI-compatible LLM implementation"""

    supported: ClassVar[str] = "openai"

    api_key: InitVar[str] = field(repr=False)
    base_url: InitVar[str]
    model_name: InitVar[str]
    temperature: InitVar[float] = 0.0

    llm: ChatOpenAI = field(init=False)

    def __post_init__(
        self,
        api_key: str,
        base_url: str,
        model_name: str,
        temperature: float,
    ) -> None:
        self.llm = ChatOpenAI(
            openai_api_key=lambda: api_key,
            openai_api_base=base_url,
            model_name=model_name,
            temperature=temperature,
            streaming=True,
        )

    @override
    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        async for chunk in self.llm.astream(prompt):
            if chunk.content:
                yield chunk.content

    @override
    async def generate(self, prompt: str) -> str | list[str | dict]:
        response = await self.llm.ainvoke(prompt)
        return response.content
