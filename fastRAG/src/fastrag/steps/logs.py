from typing import Callable, Protocol

from fastrag.constants import get_constants
from fastrag.events import Event

type LogCallback = Callable[[Event], None]


class Logger(Protocol):

    def _log(self, event: Event) -> None: ...

    def _log_verbose(self, event: Event) -> None: ...


def set_logging_callback(obj: Logger) -> None:
    object.__setattr__(
        obj,
        "_callback",
        obj._log_verbose if get_constants().verbose else obj._log,
    )
