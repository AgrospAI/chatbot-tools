import asyncio
import re
from dataclasses import InitVar, dataclass, field
from difflib import SequenceMatcher
from typing import ClassVar, override

from fastrag.config.config import Config
from fastrag.events import Event
from fastrag.llms.llm import ILLM
from fastrag.plugins import inject
from fastrag.steps.task import Run, Task


@dataclass
class Question:
    question: str
    answers: list[str]

    answer: str | None = None
    score: float = 0.0


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _string_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def _token_overlap(a: str, b: str) -> float:
    tokens_a = set(a.split())
    tokens_b = set(b.split())
    if not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_b)


def score_answer(question: Question) -> float:
    """
    Returns a score in [0.0, 1.0] indicating how well `answer`
    matches any of the acceptable answers in `question.answers`.
    """
    user = _normalize(question.answer)

    if not user or not question.answers:
        return 0.0

    best_score = 0.0

    for valid in question.answers:
        valid = _normalize(valid)

        if not valid:
            continue

        # Individual similarity measures
        edit_score = _string_similarity(user, valid)
        token_score = _token_overlap(user, valid)

        # Conservative combination
        score = max(edit_score, token_score)

        best_score = max(best_score, score)

    # Clamp defensively
    return max(0.0, min(1.0, best_score))


def _inject() -> ILLM:
    config = Config.instance
    return inject(ILLM, config.resources.llm.strategy, **config.resources.llm.params)


@dataclass(frozen=True)
class QuerySetBenchmarking(Task):
    supported: ClassVar[str] = "QuerySet"
    questions: InitVar[list[list[str]]] = field(repr=False)

    _questions: list[Question] = field(init=False, repr=False, default_factory=list)
    _score: float = field(default=0.0, repr=False)

    def __post_init__(self, questions: list[list[str]]) -> None:
        for question in questions:
            question = map(_normalize, question)
            question = Question(question=next(question), answers=list(question))
            self._questions.append(question)

    @override
    async def run(self) -> Run:
        async def process_question(question: Question) -> Question:
            # question.answer = await self._llm.generate(question.question)
            question.answer = "asd"
            question.score = score_answer(question)
            return question

        tasks = [process_question(question) for question in self._questions]
        answers = await asyncio.gather(*tasks)

        for a in answers:
            yield Event(Event.Type.PROGRESS, f"Question: {a.question}, LLM: {a.answer}")

        if self._questions:
            object.__setattr__(self, "_score", sum(a.score for a in answers) / len(answers))

    @override
    def completed_callback(self) -> Event:
        return Event(Event.Type.COMPLETED, f"Mean QuerySet response score {self._score}")
