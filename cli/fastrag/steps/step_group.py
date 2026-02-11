from __future__ import annotations

import base64
import random
import string
import uuid
from dataclasses import dataclass
from typing import override

from fastrag.helpers.experiments import Experiment
from fastrag.steps.base import IStepCommon
from fastrag.tasks.base import Task

ALPHA_UNDERSCORE = string.ascii_letters + "_"
ALPHANUM_UNDERSCORE = string.ascii_letters + string.digits + "_"


def generate_alphanum_id(experiment: IMultiStep, length: int = 22) -> str:
    # Deterministic path
    if experiment is not None:
        # Serialize and to bytes the experiment steps as seed

        rng = random.Random("".join([repr(step.tasks) for step in experiment.steps.values()]))
        return rng.choice(ALPHA_UNDERSCORE) + "".join(
            rng.choice(ALPHANUM_UNDERSCORE) for _ in range(length)
        )

    # Non-deterministic path (UUID-based)
    raw = uuid.uuid4().bytes
    encoded = base64.urlsafe_b64encode(raw).decode("ascii")
    return encoded.rstrip("=").replace("-", "_")[:length]


@dataclass
class IMultiStep(IStepCommon, Experiment):
    def __post_init__(self, *args, **kwargs) -> None:
        super().__post_init__(*args, **kwargs)

        self.hash = generate_alphanum_id(self)

        for step in self.steps.values():
            step.experiment = self

            for task in step.tasks:
                task.experiment = self

        lines = []
        for step in self.steps.values():
            step_name = step.__class__.__name__
            lines.append(f"\t{step_name}:")
            lines.append(f"\t└─ {step.tasks}")

        self._results = (
            f"Experiment  #{self.task_id + 1} | {self.hash}"
            + " | {score}:\n"
            + f"{'\n'.join(lines)}"
        )

    @property
    def results(self) -> str:
        return self._results.replace("{score}", str(self.score))

    @override
    def calculate_total(self) -> int:
        return sum(step.calculate_total() for step in self.steps.values())

    @override
    def tasks(self, step: str) -> list[Task]:
        tasks = []
        for s in self.steps.values():
            if step in s.supported:
                tasks.extend(s.tasks)

        return tasks

    @override
    def save_results(self, results: str) -> None:
        self._results += results
