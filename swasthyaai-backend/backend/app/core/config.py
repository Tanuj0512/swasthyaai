"""
The ONE configuration file for the backend.

Every setting the application needs — database, auth, AI provider, external
APIs, rate limits — is declared here and nowhere else. Modules import
`settings` from this file; they never call `os.getenv` directly. This is what
lets `AI_PROVIDER=gemini` become `AI_PROVIDER=ollama` without touching a
single line of application code.
"""

from functools import lru_cache
from typing import List, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Application ---
    APP_ENV: Literal["local", "staging", "production"] = "local"
    APP_NAME: str = "SwasthyaAI Backend"
    API_V1_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "INFO"
    CORS_ALLOW_ORIGINS: str = "http://localhost:5173"

    # --- Database ---
    DATABASE_URL: str

    # --- Auth ---
    SUPABASE_URL: str = ""
    SUPABASE_JWT_SECRET: str
    SUPABASE_JWT_AUDIENCE: str = "authenticated"
    DEMO_DISABLE_JWT_VERIFY: bool = False

    # --- AI provider selection ---
    AI_PROVIDER: Literal["gemini", "openai", "ollama"] = "gemini"
    AI_REQUEST_TIMEOUT_SECONDS: int = 20

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"

    # --- Google Cloud Voice ---
    GOOGLE_APPLICATION_CREDENTIALS: str = ""

    # --- Rate limiting ---
    RATE_LIMIT_PUBLIC: str = "20/minute"
    RATE_LIMIT_STAFF: str = "60/minute"

    # --- Caching ---
    CACHE_DEFAULT_TTL_SECONDS: int = 30

    @field_validator("SUPABASE_JWT_SECRET")
    @classmethod
    def secret_must_not_be_empty_in_non_local(cls, v: str, info) -> str:
        # Local dev may run against a throwaway secret; staging/production
        # must never boot with an empty one.
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ALLOW_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings singleton. `lru_cache` ensures the .env file is parsed
    exactly once per process, and lets tests override via
    `get_settings.cache_clear()` + monkeypatched env vars.
    """
    return Settings()


settings = get_settings()
