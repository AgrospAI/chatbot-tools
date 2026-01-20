from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

import fastrag

package_dir = Path(fastrag.__file__).parent.parent.parent
resources_dir = package_dir / "resources"
DEFAULT_CONFIG = resources_dir / "config.yaml"


class Settings(BaseSettings):
    database_url: str | None = Field(None, env="DATABASE_URL")
    milvus_user: str | None = Field(None, env="MILVUS_USER")
    milvus_password: str | None = Field(None, env="MILVUS_PASSWORD")
    chat_api_key: str | None = Field(None, env="CHAT_API_KEY")
    plugins_dir: str | None = Field(None, env="PLUGINS_DIR")
    config_path: Path = Field(DEFAULT_CONFIG, env="CONFIG_PATH")

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, url: Optional[str]) -> Optional[str]:
        if url and not url.startswith("postgresql://"):
            raise ValueError("Only PostgreSQL databases are supported")
        return url

    @field_validator("config_path", "plugins_dir")
    @classmethod
    def validate_paths(cls, paths: Optional[Path]) -> Optional[Path]:
        if paths and not paths.exists():
            raise ValueError(f"Path does not exist: {paths}")
        return paths

    class Config:
        env_file = ".env"


settings = Settings()
