"""
NeuroScrape - Application Configuration
Manages environment variables, default fallback values, and system constants.
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Environment
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["*"]

    # Bright Data Credentials
    BRIGHTDATA_API_KEY: Optional[str] = None
    BRIGHTDATA_CUSTOMER_ID: Optional[str] = None
    BRIGHTDATA_ZONE: Optional[str] = None
    BRIGHTDATA_SCRAPER_STUDIO_API_URL: str = "https://api.brightdata.com/dca/v1"

    # LLM Settings
    LLM_PROVIDER: str = "groq"  # "groq", "openai", "anthropic", "local"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-oss-120b"

    # Database & Storage
    DATABASE_URL: str = "sqlite:///./neuroscrape.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # NeuroAnchor Local Model
    MODEL_PATH: str = "./models/neuroanchor-v1-onnx"
    KARMA_MODEL_PATH: str = "./models/karma-head.joblib"
    NEUROANCHOR_CONFIDENCE_THRESHOLD: float = 0.72

    # Ethics & Guardrails
    ENFORCE_ROBOTS_TXT: bool = True
    BLOCK_PRIVATE_URLS: bool = True


settings = Settings()
