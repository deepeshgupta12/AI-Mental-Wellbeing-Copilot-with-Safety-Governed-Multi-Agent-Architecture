from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="local", alias="APP_ENV")
    app_name: str = Field(default="AI Mental Wellbeing Copilot API", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="mental_wellbeing", alias="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", alias="POSTGRES_PASSWORD")

    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_default_model: str = Field(default="llama3.2", alias="OLLAMA_DEFAULT_MODEL")

    scheduler_backend: str = Field(default="local_contract", alias="SCHEDULER_BACKEND")
    temporal_enabled: bool = Field(default=False, alias="TEMPORAL_ENABLED")
    temporal_namespace: str = Field(default="default", alias="TEMPORAL_NAMESPACE")
    temporal_task_queue: str = Field(
        default="mental-wellbeing-followups",
        alias="TEMPORAL_TASK_QUEUE",
    )

    cors_allow_origins: str = Field(
        default=(
            "http://localhost:3000,"
            "http://127.0.0.1:3000,"
            "http://localhost:8080,"
            "http://127.0.0.1:8080"
        ),
        alias="CORS_ALLOW_ORIGINS",
    )

    otel_enabled: bool = Field(default=False, alias="OTEL_ENABLED")
    otel_service_name: str = Field(
        default="mental-wellbeing-api",
        alias="OTEL_SERVICE_NAME",
    )

    # -----------------------------
    # V4 Pack 1 enterprise auth/RBAC
    # -----------------------------
    deployment_name: str = Field(default="local", alias="DEPLOYMENT_NAME")
    auth_mode: str = Field(default="development_bypass", alias="AUTH_MODE")
    auth_session_secret: str = Field(
        default="dev-session-secret-change-me",
        alias="AUTH_SESSION_SECRET",
    )
    auth_access_token_ttl_minutes: int = Field(
        default=480,
        alias="AUTH_ACCESS_TOKEN_TTL_MINUTES",
    )
    auth_header_name: str = Field(default="Authorization", alias="AUTH_HEADER_NAME")
    auth_cookie_name: str = Field(default="mwc_session", alias="AUTH_COOKIE_NAME")
    auth_allow_dev_bootstrap: bool = Field(default=True, alias="AUTH_ALLOW_DEV_BOOTSTRAP")
    auth_allow_dev_headers: bool = Field(default=True, alias="AUTH_ALLOW_DEV_HEADERS")

    enterprise_default_org_name: str = Field(
        default="Default Enterprise",
        alias="ENTERPRISE_DEFAULT_ORG_NAME",
    )
    enterprise_default_org_slug: str = Field(
        default="default-enterprise",
        alias="ENTERPRISE_DEFAULT_ORG_SLUG",
    )
    enterprise_admin_role_name: str = Field(
        default="platform_admin",
        alias="ENTERPRISE_ADMIN_ROLE_NAME",
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def cors_allow_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allow_origins.split(",")
            if origin.strip()
        ]

    @property
    def is_production_like(self) -> bool:
        return self.app_env.lower() in {"production", "prod", "staging"}

    @property
    def auth_requires_token(self) -> bool:
        return self.auth_mode == "token_required"


@lru_cache
def get_settings() -> Settings:
    return Settings()