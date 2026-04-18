"""Application configuration for the local MarketMind backend."""

from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    """Settings loaded from backend/.env and environment variables."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql+psycopg2://postgres:@localhost:5432/marketmind"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "marketmind"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    JWT_SECRET_KEY: str = Field(default="change-this-before-using-real-auth")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FRONTEND_URL: str = "http://127.0.0.1:5173"

    @property
    def FRONTEND_ORIGINS(self) -> list[str]:
        origins = {self.FRONTEND_URL.rstrip("/")}
        parsed = urlsplit(self.FRONTEND_URL)

        alternate_host = None
        if parsed.hostname == "localhost":
            alternate_host = "127.0.0.1"
        elif parsed.hostname == "127.0.0.1":
            alternate_host = "localhost"

        if alternate_host:
            netloc = alternate_host
            if parsed.port is not None:
                netloc = f"{alternate_host}:{parsed.port}"
            origins.add(urlunsplit((parsed.scheme, netloc, "", "", "")))

        return sorted(origins)


@lru_cache
def get_settings() -> Settings:
    return Settings()
