"""Configuration settings for the Budget App.

Security: All secrets loaded from environment variables, never hardcoded.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with secure defaults."""

    # Database
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "budget_app"

    # Security - CRITICAL: Must be set in production
    secret_key: str  # Required, no default for security
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global settings instance
# Security: Loads from environment variables
settings = Settings()
