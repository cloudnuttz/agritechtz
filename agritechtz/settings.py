"""Settings Module"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Base settings module"""

    database_url: str
    redis_backend_url: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Retrieve a single instance of the `Settings` class"""
    return Settings()
