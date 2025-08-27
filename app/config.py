from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "agent_orchestration"
    
    # API
    api_version: str = "v1"
    cors_origins: List[str] = ["*"]  # maps from CORS_ORIGINS
    
    # Monitoring
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    
    # Model API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    perplexity_api_key: str = ""
    
    # AWS
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""       # NEW
    aws_secret_access_key: str = ""   # NEW
    
    # Redis
    redis_url: str = "redis://localhost:6379"  # NEW
    
    # Service
    environment: str = "development"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
