from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from fastrag.settings import DEFAULT_CONFIG


class Settings(BaseSettings):
    database_url: str | None = Field(None, env="DATABASE_URL")
    milvus_user: str | None = Field(None, env="MILVUS_USER")
    milvus_password: str | None = Field(None, env="MILVUS_PASSWORD")
    chat_api_key: str | None = Field(None, env="CHAT_API_KEY")
    fastrag_plugins_dir: str | None = Field(None, env="FASTRAG_PLUGINS_DIR")
    fastrag_config_path: Path = Field(DEFAULT_CONFIG, env="FASTRAG_CONFIG_PATH")

    class Config:
        env_file = ".env"


settings = Settings()
