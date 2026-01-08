import re
from datetime import datetime
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as v
from typing import TypeAlias
from urllib.parse import urlparse, urlunparse


def version(package_name: str) -> str:
    try:
        return v(package_name)
    except PackageNotFoundError:
        return "???"


def parse_to_seconds(time: str) -> int:
    """Parse time string to int seconds

    Args:
        time (str): time string to parse

    Returns:
        int: seconds representation of given time
    """

    UNITS = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400,
    }

    pattern = r"(\d+)([smhd])"
    total_seconds = 0

    try:
        for value, unit in re.findall(pattern, time):
            total_seconds += int(value) * UNITS[unit]
    except KeyError as e:
        raise ValueError("Unsupported time unit") from e

    return total_seconds


PosixTimestamp: TypeAlias = float


def timestamp() -> PosixTimestamp:
    return datetime.now().timestamp()


def normalize_url(url: str) -> str:
    # Parse the URL into components
    parsed = urlparse(url)

    # Normalize path: ensure it ends with a single trailing slash
    path = parsed.path
    if not path.endswith("/"):
        path += "/"

    # Remove duplicate slashes
    while "//" in path:
        path = path.replace("//", "/")

    # Reconstruct the URL
    normalized = urlunparse(
        (
            parsed.scheme.lower(),  # normalize scheme
            parsed.netloc.lower(),  # normalize host
            path,
            "",  # params
            "",  # query
            "",  # fragment
        )
    )
    return normalized
