from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.models.schemas import ModelConfig, MCPServerConfig, ToolConfig  # import from schemas


class AgentConfiguration(Document):
    agent_id: str = Field(..., description="Unique agent identifier")
    name: str
    description: Optional[str] = None
    system_prompt: str
    agent_model_config: ModelConfig
    mcp_servers: List[MCPServerConfig] = []
    tools: List[ToolConfig] = []
    builtin_tools: List[str] = []
    timeout: int = 300
    retry_policy: Dict[str, Any] = {"max_attempts": 3, "backoff": "exponential"}
    chunking_enabled: bool = False
    chunk_size: int = 1000
    capabilities: List[str] = []
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    version: int = 1

    class Settings:
        name = "agent_configurations"
