"""
NeuroScrape - Application Configuration
Manages environment variables, default fallback values, and system constants.
"""

from typing import List, Optional, Union
import json
from pydantic import Field, field_validator
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
    CORS_ORIGINS: Union[List[str], str] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v or v == "*":
                return ["*"]
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]

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
    LLM_MODEL: str = "openai/gpt-oss-120b"

    # Database & Storage
    DATABASE_URL: str = "sqlite:///./neuroscrape.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # NeuroAnchor Local Model
    MODEL_PATH: str = "./models/neuroanchor-v1-onnx-int8"
    KARMA_MODEL_PATH: str = "./models/karma-head.joblib"
    NEUROANCHOR_CONFIDENCE_THRESHOLD: float = 0.72

    # Ethics & Guardrails
    ENFORCE_ROBOTS_TXT: bool = False
    BLOCK_PRIVATE_URLS: bool = True

    # NeuroWatch — Continuous Automation Mode
    WATCH_INTERVAL_SECONDS: int = 120
    WATCH_MAX_SOURCES: int = 5

    # NeuroAnchor Collective Memory (Cross-Site Immune System)
    MEMORY_PREFETCH_THRESHOLD: float = 0.75


settings = Settings()

