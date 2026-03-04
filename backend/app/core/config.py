"""Application configuration."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    app_name: str = "AgentPPT"
    debug: bool = False
    data_dir: str = "../data"
    max_upload_size_mb: int = 20
    
    # OpenAI
    openai_api_key: Optional[str] = None
    openai_api_base: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4-turbo-preview"
    
    # Anthropic
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-opus-20240229"
    
    # Default LLM provider: "openai" or "anthropic"
    llm_provider: str = "openai"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()