from dataclasses import dataclass
from typing import AsyncGenerator, Iterable, override

from fastrag.parsing.parser import IParser, ParsingEvent


@dataclass(frozen=True)
class HtmlParser(IParser):

    use: list[str]

    @override
    @classmethod
    def supported(cls) -> Iterable[str]:
        return ["HtmlParser"]

    @override
    async def parse(self) -> AsyncGenerator[ParsingEvent, None]:

        yield ParsingEvent(ParsingEvent.Type.COMPLETED, "Completed HTML Parsing")
