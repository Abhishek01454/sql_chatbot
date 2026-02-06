"""
Core configuration module for the application.
Manages all environment variables and application settings.
"""

from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import os
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Settings
    APP_NAME: str = "CORE AI Chatbot API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Enterprise-grade AI chatbot API with Mistral AI integration"
    DEBUG: bool = False
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")

    # CORS Settings
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS"
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Security Settings
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    ALGORITHM: str = "HS256"

    # Database Settings
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")

    # Redis Settings (for caching and sessions)
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")

    # Mistral AI Settings
    MISTRAL_API_KEY: str = Field(..., env="MISTRAL_API_KEY")
    MISTRAL_API_URL: str = Field(
        default="https://api.mistral.ai/v1/chat/completions",
        env="MISTRAL_API_URL"
    )
    MISTRAL_MODEL: str = Field(
        default="mistral-small-latest",
        env="MISTRAL_MODEL"
    )
    MISTRAL_MAX_TOKENS: int = Field(default=4096, env="MISTRAL_MAX_TOKENS")
    MISTRAL_TEMPERATURE: float = Field(default=0.7, env="MISTRAL_TEMPERATURE")
    MISTRAL_TIMEOUT: int = Field(default=120, env="MISTRAL_TIMEOUT")

    # AWS Bedrock Settings (alternative AI provider)
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: Optional[str] = Field(default="us-east-1", env="AWS_REGION")
    BEDROCK_MODEL_ID: Optional[str] = Field(
        default="anthropic.claude-3-haiku-20240307-v1:0",
        env="BEDROCK_MODEL_ID"
    )

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")

    # Logging Settings
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="logs/app.log", env="LOG_FILE")
    LOG_MAX_BYTES: int = Field(default=10485760, env="LOG_MAX_BYTES")  # 10MB
    LOG_BACKUP_COUNT: int = Field(default=5, env="LOG_BACKUP_COUNT")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Monitoring & Metrics
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")

    # Session & Cache Settings
    SESSION_TIMEOUT_MINUTES: int = Field(default=60, env="SESSION_TIMEOUT_MINUTES")
    CACHE_TTL_SECONDS: int = Field(default=3600, env="CACHE_TTL_SECONDS")

    # Conversation Settings
    MAX_CONVERSATION_HISTORY: int = Field(default=50, env="MAX_CONVERSATION_HISTORY")
    MAX_MESSAGE_LENGTH: int = Field(default=10000, env="MAX_MESSAGE_LENGTH")
    DEFAULT_SYSTEM_PROMPT: str = Field(
        default="You are a helpful AI assistant. You are knowledgeable, helpful, and provide accurate, well-structured responses.",
        env="DEFAULT_SYSTEM_PROMPT"
    )

    # File Upload Settings (for future features)
    MAX_UPLOAD_SIZE_MB: int = Field(default=10, env="MAX_UPLOAD_SIZE_MB")
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = Field(
        default=[".txt", ".pdf", ".doc", ".docx"],
        env="ALLOWED_UPLOAD_EXTENSIONS"
    )

    # Worker Settings (for background tasks)
    CELERY_BROKER_URL: Optional[str] = Field(default=None, env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: Optional[str] = Field(default=None, env="CELERY_RESULT_BACKEND")

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v

    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Validate environment."""
        valid_envs = ["development", "staging", "production", "testing"]
        v = v.lower()
        if v not in valid_envs:
            raise ValueError(f"ENVIRONMENT must be one of {valid_envs}")
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.ENVIRONMENT == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing."""
        return self.ENVIRONMENT == "testing"

    @property
    def database_enabled(self) -> bool:
        """Check if database is configured."""
        return self.DATABASE_URL is not None

    @property
    def redis_enabled(self) -> bool:
        """Check if Redis is configured."""
        return self.REDIS_URL is not None

    @property
    def aws_bedrock_enabled(self) -> bool:
        """Check if AWS Bedrock is configured."""
        return all([
            self.AWS_ACCESS_KEY_ID,
            self.AWS_SECRET_ACCESS_KEY,
            self.AWS_REGION
        ])

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()


# Global settings instance
settings = get_settings()
