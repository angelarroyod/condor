"""Application configuration via pydantic-settings.

Every value is overridable by an environment variable of the same (upper-cased)
name. See ``.env.example`` for the documented set. No secrets live in code.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Infrastructure ---
    database_url: str = Field(
        default="postgresql+asyncpg://condor:condor@localhost:5432/condor",
        description="Async SQLAlchemy DSN (asyncpg driver).",
    )
    redis_url: str = Field(default="redis://localhost:6379/0")

    # --- Market data ---
    binance_ws_url: str = Field(default="wss://stream.binance.com:9443/stream")
    symbols: str = Field(
        default="BTCUSDT,ETHUSDT,SOLUSDT",
        description="Comma-separated crypto symbols the ingest worker subscribes to.",
    )

    # --- API ---
    cors_origins: str = Field(default="http://localhost:5173")
    log_level: str = Field(default="INFO")
    log_json: bool = Field(default=True, description="Emit JSON logs (False = key=value).")

    @property
    def symbol_list(self) -> list[str]:
        return [s.strip().upper() for s in self.symbols.split(",") if s.strip()]

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton. ``lru_cache`` = one parse per process."""
    return Settings()
