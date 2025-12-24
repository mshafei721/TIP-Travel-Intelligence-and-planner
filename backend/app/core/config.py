"""Application configuration using Pydantic Settings"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "TIP"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # API
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_JWT_SECRET: str
    DATABASE_URL: str

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str
    SESSION_LIFETIME_HOURS: int = 24
    RATE_LIMIT_PER_MINUTE: int = 60

    # Application Settings
    TRIP_DATA_RETENTION_DAYS: int = 30
    GDPR_ENABLED: bool = True
    LOG_LEVEL: str = "INFO"

    # Feature Flags
    FEATURE_DASHBOARD_HOME: bool = True
    FEATURE_RECOMMENDATIONS: bool = True
    FEATURE_ANALYTICS: bool = True

    # External APIs
    RAPIDAPI_KEY: str  # Travel Buddy AI / Sherpa API
    ANTHROPIC_API_KEY: str  # Claude AI for CrewAI agents

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = "../.env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables not defined in model


# Global settings instance
settings = Settings()
