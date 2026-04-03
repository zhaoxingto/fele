from pathlib import Path

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    app_name: str = Field(default="fele-erp", validation_alias="FELE_APP_NAME")
    app_env: str = Field(default="development", validation_alias="FELE_APP_ENV")
    debug: bool = Field(default=True, validation_alias="FELE_DEBUG")
    api_prefix: str = Field(default="/api/v1", validation_alias="FELE_API_PREFIX")
    database_url: str = Field(default="sqlite:///./fele.db", validation_alias="FELE_DATABASE_URL")
    super_admin_email: str = Field(
        default="admin@fele.local", validation_alias="FELE_SUPER_ADMIN_EMAIL"
    )
    super_admin_password: str = Field(
        default="Admin@123456", validation_alias="FELE_SUPER_ADMIN_PASSWORD"
    )
    super_admin_name: str = Field(
        default="Fele Super Admin", validation_alias="FELE_SUPER_ADMIN_NAME"
    )

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
