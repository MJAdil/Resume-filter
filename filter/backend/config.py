"""Application configuration management"""
import os
import logging
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Required settings
    mongodb_uri: str = Field(..., env='MONGODB_URI')
    
    # Optional settings
    github_token: Optional[str] = Field(None, env='GITHUB_TOKEN')
    linkedin_api_key: Optional[str] = Field(None, env='LINKEDIN_API_KEY')
    linkedin_provider: str = Field('scrapingdog', env='LINKEDIN_PROVIDER')
    
    # Application settings
    environment: str = Field('development', env='ENVIRONMENT')
    log_level: str = Field('INFO', env='LOG_LEVEL')
    
    # Model settings
    embedding_model: str = Field('BAAI/bge-small-en-v1.5', env='EMBEDDING_MODEL')
    
    class Config:
        env_file = '.env'
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings"""
    return Settings()


def log_configuration(settings: Settings) -> None:
    """Log configuration status at startup"""
    logger.info("=" * 60)
    logger.info("Configuration Status")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Log Level: {settings.log_level}")
    logger.info(f"MongoDB URI: {'✓ Configured' if settings.mongodb_uri else '✗ Not set'}")
    logger.info(f"GitHub Token: {'✓ Configured' if settings.github_token else '✗ Not set (rate limited)'}")
    logger.info(f"LinkedIn API Key: {'✓ Configured' if settings.linkedin_api_key else '✗ Not set'}")
    logger.info(f"Embedding Model: {settings.embedding_model}")
    logger.info("=" * 60)
