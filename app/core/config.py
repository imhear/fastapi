# app/core/config.py
import os
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE_PATH", ".env"),
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "FastAPI Project"
    ENVIRONMENT: str = Field("local", env="ENVIRONMENT")

    POSTGRES_SERVER: str = Field("localhost", env="POSTGRES_SERVER")
    POSTGRES_PORT: int = Field(5432, env="POSTGRES_PORT")
    POSTGRES_USER: str = Field("postgres", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field("", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field("", env="POSTGRES_DB")

    DB_POOL_SIZE: int = Field(20)
    DB_MAX_OVERFLOW: int = Field(100)
    DB_POOL_RECYCLE: int = Field(3600)
    DB_POOL_PRE_PING: bool = Field(True)

    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_DB: int = Field(0, env="REDIS_DB")
    REDIS_PASSWORD: str = Field("", env="REDIS_PASSWORD")
    REDIS_ENCODING: str = Field("utf-8", env="REDIS_ENCODING")
    REDIS_DECODE_RESPONSES: bool = Field(True, env="REDIS_DECODE_RESPONSES")
    REDIS_MAX_CONNECTIONS: int = Field(10, env="REDIS_MAX_CONNECTIONS")
    REDIS_USE_POOL: bool = Field(True, env="REDIS_USE_POOL")
    REDIS_SOCKET_TIMEOUT: int = Field(5, env="REDIS_SOCKET_TIMEOUT")
    REDIS_SOCKET_CONNECT_TIMEOUT: int = Field(5, env="REDIS_SOCKET_CONNECT_TIMEOUT")

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()