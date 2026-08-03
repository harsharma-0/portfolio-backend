from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "Harsh Portfolio API"
    app_env: str = "development"
    app_version: str = "1.0.0"
    debug: bool = False
    api_prefix: str = "/api/v1"
    frontend_origins: str = "http://localhost:4200"
    resend_api_key: str = ""
    email_from: str = ""
    contact_receiver_email: str = ""
    max_request_bytes: int = 1_000_000

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        value = self.frontend_origins.strip()
        if value.startswith("["):
            import json
            parsed = json.loads(value)
            if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
                raise ValueError("FRONTEND_ORIGINS JSON must be a list of strings")
            origins = parsed
        else:
            origins = value.split(",")
        return [origin.strip().rstrip("/") for origin in origins if origin.strip()]

    @property
    def email_configured(self) -> bool:
        return all(
            value.strip()
            for value in (
                self.resend_api_key,
                self.email_from,
                self.contact_receiver_email,
            )
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
