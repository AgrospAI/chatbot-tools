from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

import fastrag

package_dir = Path(fastrag.__file__).parent.parent
resources_dir = package_dir / "resources"
DEFAULT_CONFIG = resources_dir / "config.yaml"


class Settings(BaseSettings):
    database_url: Optional[str] = Field(None, env="DATABASE_URL")
    milvus_user: Optional[str] = Field(None, env="MILVUS_USER")
    milvus_password: Optional[str] = Field(None, env="MILVUS_PASSWORD")
    chat_api_key: Optional[str] = Field(None, env="CHAT_API_KEY")
    plugins_dir: Optional[Path] = Field(None, env="PLUGINS_DIR")
    config_path: Path = Field(DEFAULT_CONFIG, env="CONFIG_PATH")

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.startswith("postgresql://"):
            raise ValueError("Only PostgreSQL databases are supported")
        return v

    @field_validator("config_path", "plugins_dir", mode="before")
    @classmethod
    def validate_paths(cls, v):
        if v is None:
            return v

        path = Path(v)
        if not path.exists():
            raise ValueError(f"Path does not exist: {path}")

        return path

    model_config = SettingsConfigDict(
        env_file=".env",
    )


settings = Settings()
