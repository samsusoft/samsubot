# backend/apps/core/settings.py
# Settings for the application using Pydantic for configuration management  
"""Settings for the application using Pydantic for configuration management"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # JWT Settings
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database URLs
    DATABASE_URL: Optional[str] = None
    MONGO_URI: str = "mongodb://samsu:secret123@samsubot_mongodb:27017/samsubot?authSource=samsubot"
    REDIS_URL: Optional[str] = None

    # LLM Settings
    OLLAMA_MODEL: str = "mistral"
    SAMSUBOT_LLM_API_URL: str = "http://samsubot_llm:11434"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings()
