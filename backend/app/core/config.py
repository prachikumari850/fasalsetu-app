from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from urllib.parse import quote, unquote, urlsplit, urlunsplit


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

    @field_validator("database_url", mode="before")
    @classmethod
    def escape_database_credentials(cls, value: str) -> str:
        """Make a DATABASE_URL safe when its password contains URL characters.

        Supabase passwords commonly contain characters such as ``@``.  An
        unescaped value makes asyncpg interpret part of the password as the
        host, leading to a misleading ``getaddrinfo failed`` error.  This
        normalizes only the user-info portion; hostname, port and database are
        left untouched and no credential is logged.
        """
        if not isinstance(value, str):
            return value
        parts = urlsplit(value)
        if not parts.hostname or parts.username is None:
            return value
        username = quote(unquote(parts.username), safe="")
        password = quote(unquote(parts.password or ""), safe="")
        host = parts.hostname
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"
        netloc = f"{username}:{password}@{host}"
        if parts.port:
            netloc += f":{parts.port}"
        return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))

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
