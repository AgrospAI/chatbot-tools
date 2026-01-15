import asyncio
import json
import re
from dataclasses import InitVar, dataclass, field
from difflib import SequenceMatcher
from typing import ClassVar, override

from fastrag.events import Event
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


def build_prompt(context: str, question: str) -> str:
    """
    Construye el prompt RAG para el LLM.
    """
    return f"""
    You are a helpful assistant and expert in data spaces.

    Always use inline references in the form [<NUMBER OF DOCUMENT>](ref:<NUMBER OF DOCUMENT>)
    ONLY if you use information from a document. For example, if you use the information from
    Document[3], you should write [3](ref:3) at the end of the sentence where you used that
    information.
    Give a precise, accurate and structured answer without repeating the question.
    
    These are the documents:
    {context}

    Question:
    {question}

    Answer:
    """.strip()


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
            query_embedding = await self.store.embed_query(question.question)

            # Search for similar documents
            results = await self.store.similarity_search(
                query=question.question, query_embedding=query_embedding, k=5
            )

            context_parts = [
                f"Document[{i}]: {doc.page_content}" for i, doc in enumerate(results)
            ]
            context = "\n\n".join(context_parts)

            async def generate():
                prompt = build_prompt(context, question.question)
                return await self.llm.generate(prompt)

            question.answer = await generate()
            question.score = score_answer(question)
            return question

        tasks = [process_question(question) for question in self._questions]
        answers = await asyncio.gather(*tasks)

        for a in answers:
            yield Event(Event.Type.PROGRESS, f"Question: {a.question}, LLM: {a.answer}")

        overall_score = sum(a.score for a in answers) / len(answers)
        self.experiment.save_results(f"\nQuerySetBenchmarking overall score: {overall_score}")

        if self._questions:
            object.__setattr__(self, "_score", overall_score)

    @override
    def completed_callback(self) -> Event:
        return Event(Event.Type.COMPLETED, f"Mean QuerySet response score {self._score}")
