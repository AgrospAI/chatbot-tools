from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(..., env="DATABASE_URL")
    milvus_user: str = Field(..., env="MILVUS_USER")
    milvus_password: str = Field(..., env="MILVUS_PASSWORD")
    chat_api_key: str = Field(..., env="CHAT_API_KEY")

    class Config:
        env_file = ".env"


settings = Settings()
