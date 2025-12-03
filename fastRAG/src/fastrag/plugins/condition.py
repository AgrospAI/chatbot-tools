from typing import Protocol


class Condition(Protocol):
    def check(self, name: str) -> bool: ...
