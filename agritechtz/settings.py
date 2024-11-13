"""Settings Module"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Base settings module"""

    database_url: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
