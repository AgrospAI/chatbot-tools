from enum import StrEnum, auto


class System(StrEnum):
    CACHE = auto()
    CONFIG_LOADER = auto()
    RUNNER = auto()
    STEP = auto()
    FETCHING = auto()
    PARSING = auto()
    CHUNKING = auto()
    EMBEDDING = auto()
    BENCHMARKING = auto()
