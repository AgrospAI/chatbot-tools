import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import ClassVar, Dict, List, override

import numpy as np
from langchain_core.documents import Document

from fastrag.events import Event
from fastrag.steps.task import Run, Task


def calculate_corpus_quality(docs: List[Document]) -> Dict:
    if not docs:
        return {}

    # 1. Calculate Global Statistics
    lengths = [len(d.page_content) for d in docs]
    stats = {"mean": np.mean(lengths), "std": np.std(lengths), "total_docs": len(docs)}

    results = []

    # 2. Evaluate each document
    for doc in docs:
        # Internal Score (Structure, Metadata, Purity)
        local_score = evaluate_document_quality(doc)

        # Relative Score (Length Z-Score)
        relative_score = evaluate_relative_quality(doc, stats)

        # Composite Score (70% Internal / 30% Relative)
        final_score = round((local_score * 0.7) + (relative_score * 0.3), 2)

        results.append({"score": final_score})

    # 3. Aggregate Corpus Metrics
    scores = [r["score"] for r in results]
    overall_report = {
        "average_quality": float(round(np.mean(scores), 2)),
        "median_quality": float(round(np.median(scores), 2)),
        "min_quality": min(scores),
        "max_quality": max(scores),
        "low_quality_count": sum(1 for s in scores if s < 0.5),
    }

    return overall_report


def calculate_corpus_stats(docs: list[Document]):
    """Pre-calculate the mean and std of the document lengths."""
    lengths = [len(d.page_content) for d in docs]
    return {"mean": np.mean(lengths), "std": np.std(lengths)}


def evaluate_relative_quality(doc: Document, stats: dict) -> float:
    """
    Scores a document based on how it fits within the corpus distribution.
    Returns 0.0 to 1.0.
    """
    length = len(doc.page_content)

    # Calculate Z-score: (x - mean) / std
    z_score = (length - stats["mean"]) / stats["std"]

    # 1. Length Consistency Score
    # We want chunks to be within -1.0 and +1.5 standard deviations.
    # Too small (negative z) is usually worse than too large (positive z).
    if -1.0 <= z_score <= 1.5:
        rel_score = 1.0
    elif z_score < -1.5:  # Way too small compared to average
        rel_score = 0.3
    elif z_score > 2.0:  # Way too large compared to average
        rel_score = 0.5
    else:
        rel_score = 0.7

    return rel_score


def evaluate_document_quality(doc: Document) -> float:
    """
    Evaluates a LangChain Document for RAG suitability.
    Returns a score between 0.0 (poor) and 1.0 (excellent).
    """
    score = 0.0
    # Weighted criteria
    weights = {
        "length_reliability": 0.25,
        "structural_richness": 0.30,
        "metadata_depth": 0.25,
        "content_purity": 0.20,
    }

    text = doc.page_content
    meta = doc.metadata
    char_len = len(text)

    # 1. Length Reliability (0.25)
    # Penalize chunks that are too fragmented (<150) or overly massive (>4000)
    if 400 <= char_len <= 2500:
        score += weights["length_reliability"]
    elif 150 < char_len < 4000:
        score += weights["length_reliability"] * 0.6

    # 2. Structural Richness (0.30)
    # Checks for Markdown markers that help LLMs parse hierarchy
    has_bold = 1 if "**" in text else 0
    has_lists = 1 if re.search(r"\n\s*(\d+[.-]|[*+-])\s", text) else 0
    has_newlines = 1 if text.count("\n") > 2 else 0

    struct_score = (has_bold * 0.3) + (has_lists * 0.4) + (has_newlines * 0.3)
    score += struct_score * weights["structural_richness"]

    # 3. Metadata Depth (0.25)
    # Quality RAG requires knowing where the info came from
    essential_fields = ["source", "title_path", "chunk_id"]
    fields_found = sum(1 for field in essential_fields if field in meta)

    score += (fields_found / len(essential_fields)) * weights["metadata_depth"]

    # 4. Content Purity (0.20)
    # High-quality chunks have a high ratio of alphanumeric characters vs symbols/whitespace
    if char_len > 0:
        alnum_chars = sum(c.isalnum() for c in text)
        alnum_ratio = alnum_chars / char_len
        # Ideal ratio is usually 0.6 to 0.9. If too low, it's likely code/tables/noise.
        if 0.6 <= alnum_ratio <= 0.95:
            score += weights["content_purity"]
        else:
            score += (alnum_ratio) * weights["content_purity"]

    return round(score, 2)


@dataclass(frozen=True)
class ChunkQualityBenchmarking(Task):
    supported: ClassVar[str] = "ChunkQuality"

    _quality: dict = field(default_factory=dict, repr=False)

    @override
    async def run(self) -> Run:
        chunking_tasks = self.experiment.tasks("chunking")

        qualities = []
        total = 0

        for task in chunking_tasks:
            for documents in task.results:
                docs = []
                for doc in documents:
                    docs.append(
                        Document(
                            page_content=doc["page_content"],
                            metadata={
                                **doc["metadata"],
                                "chunk_id": doc["chunk_id"],
                                "level": doc["level"],
                            },
                        )
                    )
                total += 1

                quality = calculate_corpus_quality(docs)
                qualities.append(quality)

                yield Event(
                    Event.Type.PROGRESS, f"Calculated quality of {len(documents)} chunks"
                )

        overall = defaultdict(float)
        for quality in qualities:
            for k, v in quality.items():
                overall[f"{k}_mean"] += v

        for k, v in overall.items():
            overall[k] = round(v / total, 3)

        self.experiment.save_results(
            f"\nChunkQualityBenchmarking ({total} docs): {json.dumps(overall, indent=4)}"
        )
        object.__setattr__(self, "_quality", quality)

    @override
    def completed_callback(self) -> Event:
        return Event(Event.Type.COMPLETED, f"Overall chunking quality {self._quality}")
