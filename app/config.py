from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # MongoDB - Master Database
    mongodb_url: str = "mongodb://localhost:27017"
    master_database_name: str = "ktern-masterdb"
    
    # Project Database Pattern
    project_database_prefix: str = "ktern-project-"
    
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
    
    # ERP Exception Management
    mcp_abap_server_path: str = ""    # Path to SAP MCP server
    erp_reports_directory: str = "erp_exception_reports"
    
    # Redis
    redis_url: str = "redis://localhost:6379"  # NEW
    
    # Service
    environment: str = "development"
    log_level: str = "INFO"
    
    # Multi-tenant settings
    enable_multi_tenant: bool = True
    default_project_id: str = "default"
    
    class Config:
        env_file = ".env"

settings = Settings()
