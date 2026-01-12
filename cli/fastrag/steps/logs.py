from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, ClassVar

from fastrag.events import Event


@dataclass
class Loggable(ABC):
    log: Callable[[Event], None] = field(init=False, repr=False)

    is_verbose: ClassVar[bool] = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "log", self.log_verbose if Loggable.is_verbose else self.log_normal
        )

    @abstractmethod
    def log_normal(self, event: Event) -> None:
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
