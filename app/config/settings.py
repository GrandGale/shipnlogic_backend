"""This module contains the settings for the application."""

import os
from functools import lru_cache


from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """The settings for the application."""

    # Import env variables during dev from .env
    model_config = SettingsConfigDict(env_file=".env")

    # Security
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    HASHING_ALGORITHM: str = os.environ.get("HASHING_ALGORITHM")

    # Token
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_HOURS: int = os.environ.get("REFRESH_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_HOURS_LONG: int = os.environ.get("REFRESH_TOKEN")

    # DB Settings
    POSTGRES_DATABASE_URL: str = os.environ.get("POSTGRES_DATABASE_URL")


@lru_cache
def get_settings():
    """This function returns the settings obj for the application."""
    return Settings()
