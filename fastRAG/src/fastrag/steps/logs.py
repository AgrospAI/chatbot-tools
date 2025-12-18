from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

from fastrag.constants import get_constants
from fastrag.events import Event


@dataclass(frozen=True)
class Loggable(ABC):

    callback: Callable[[Event], None] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "callback",
            self.log_verbose if get_constants().verbose else self.log,
        )

    @abstractmethod
    def log(self, event: Event) -> None:
        """Log the given event. Not verbose.

        Args:
            event (Event): step event
        """

        raise NotImplementedError

    @abstractmethod
    def log_verbose(self, event: Event) -> None:
        """Verbose log the given event.

        Args:
            event (Event): step event
        """

        raise NotImplementedError
