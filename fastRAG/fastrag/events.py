from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum, auto


@dataclass(frozen=True)
class Event:
    class Type(StrEnum):
        COMPLETED = auto()
        EXCEPTION = auto()
        PROGRESS = auto()

    type: Event.Type
    data: any
