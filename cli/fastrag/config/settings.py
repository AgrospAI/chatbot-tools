from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str | None = Field(None, env="DATABASE_URL")
    milvus_user: str | None = Field(None, env="MILVUS_USER")
    milvus_password: str | None = Field(None, env="MILVUS_PASSWORD")
    chat_api_key: str | None = Field(None, env="CHAT_API_KEY")

    class Config:
        env_file = ".env"


settings = Settings()
