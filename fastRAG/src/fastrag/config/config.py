from dataclasses import asdict
from pathlib import Path

from pydantic import field_validator
from pydantic.dataclasses import dataclass


class ConfigError(Exception): ...


@dataclass(frozen=True)
class Config:

    plugins: Path

    asdict = asdict

    @field_validator("plugins", mode="after")
    @classmethod
    def exists(cls, value: Path) -> Path:
        if not value.exists():
            raise ConfigError(f"'plugins' path '{value}' does not exist")
        return value
