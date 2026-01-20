from datetime import datetime
from typing import TypeAlias

PosixTimestamp: TypeAlias = float


def timestamp() -> PosixTimestamp:
    return datetime.now().timestamp()
