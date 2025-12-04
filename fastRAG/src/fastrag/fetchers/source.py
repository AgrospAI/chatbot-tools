from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    type: str
    value: str
