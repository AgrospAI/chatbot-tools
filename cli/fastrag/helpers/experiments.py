from __future__ import annotations

from typing import TypeAlias

from fastrag.steps.step import IMultiStep

Experiment: TypeAlias = IMultiStep
Experiments: TypeAlias = list[Experiment]
