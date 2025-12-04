from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from pydantic import field_validator
from pydantic.dataclasses import dataclass


class ConfigError(Exception): ...


@dataclass(frozen=True)
class Config:

    test: str
    plugins: Path | None = None

    asdict = asdict

    @field_validator("plugins", mode="after")
    @classmethod
    def exists(cls, value: Path | None) -> Path:
        if not value:
            return value

        if not value.exists():
            raise ConfigError(f"'plugins' path '{value}' does not exist")
        return value
