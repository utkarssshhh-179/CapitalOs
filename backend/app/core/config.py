from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_DEFAULT_SECRET = "change-me-in-production"  # noqa: S105


class Settings(BaseSettings):
    """Typed application settings. Every value is overridable via CAPITALOS_* env vars."""

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="CAPITALOS_", extra="ignore", case_sensitive=False
    )

    app_name: str = "CapitalOS"
    app_version: str = "0.1.0"
    environment: Literal["local", "test", "staging", "production"] = "local"
    debug: bool = False
    log_level: str = "INFO"
    log_json: bool = True

    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    database_url: str = "postgresql+asyncpg://capitalos:capitalos@localhost:5432/capitalos"
    db_pool_size: int = 10
    db_max_overflow: int = 10
    db_pool_timeout_seconds: int = 30
    db_echo: bool = False

    redis_url: str = "redis://localhost:6379/0"

    secret_key: SecretStr = SecretStr(_INSECURE_DEFAULT_SECRET)

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @model_validator(mode="after")
    def _enforce_production_safety(self) -> "Settings":
        if self.environment in {"staging", "production"}:
            if self.secret_key.get_secret_value() == _INSECURE_DEFAULT_SECRET:
                raise ValueError("CAPITALOS_SECRET_KEY must be set outside local/test")
            if len(self.secret_key.get_secret_value()) < 32:
                raise ValueError("CAPITALOS_SECRET_KEY must be at least 32 characters")
        if self.is_production and self.debug:
            raise ValueError("debug must be disabled in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
