from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    supabase_jwt_secret: str

    # Database
    database_url: str

    # App
    app_env: str = "development"
    app_secret_key: str
    app_name: str = "FasalSetu API"
    app_version: str = "1.0.0"
    allowed_origins: str = "http://localhost:5173"

    # External APIs
    open_meteo_base_url: str = "https://archive-api.open-meteo.com/v1"

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()