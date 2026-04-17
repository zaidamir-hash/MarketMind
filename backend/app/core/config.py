"""Configuration placeholders for local MarketMind backend setup."""

from dataclasses import dataclass
import os


@dataclass
class Settings:
    environment: str = os.getenv("MARKETMIND_ENV", "local")
    database_url: str = os.getenv("DATABASE_URL", "")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")


settings = Settings()
