from enum import StrEnum, auto


class System(StrEnum):
    # Core
    CACHE = auto()
    RUNNER = auto()
    STEP = auto()

    # Steps
    FETCHING = auto()
    PARSING = auto()
    CHUNKING = auto()
    EMBEDDING = auto()
    BENCHMARKING = auto()

    # Helpers / Others
    CONFIG_LOADER = auto()
    RATE_LIMITING = auto()
