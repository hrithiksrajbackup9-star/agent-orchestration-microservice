from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

from app.models.schemas import ModelConfig, MCPServerConfig, ToolConfig  # import from schemas

class AgentTemplate(Document):
    """Template for creating agents with predefined configurations"""
    template_id: str = Field(..., description="Unique template identifier")
    name: str
    description: Optional[str] = None
    category: str = Field(..., description="Agent category (e.g., ERP, Finance, etc.)")
    system_prompt_template: str = Field(..., description="System prompt with placeholders")
    default_model_config: ModelConfig
    default_mcp_servers: List[MCPServerConfig] = []
    default_tools: List[ToolConfig] = []
    default_builtin_tools: List[str] = []
    template_variables: Dict[str, Any] = Field(default_factory=dict, description="Variables for prompt templating")
    capabilities: List[str] = []
    tags: List[str] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "agent_templates"

class SystemPromptTemplate(Document):
    """Configurable system prompts with variables"""
    template_id: str = Field(..., description="Unique template identifier")
    name: str
    description: Optional[str] = None
    template_content: str = Field(..., description="Prompt template with {{variable}} placeholders")
    variables: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Variable definitions with types and defaults")
    category: str = Field(..., description="Template category")
    version: str = "1.0.0"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "system_prompt_templates"

class MCPServerRegistry(Document):
    """Registry of available MCP servers"""
    server_id: str = Field(..., description="Unique server identifier")
    name: str
    description: Optional[str] = None
    server_type: str = Field(..., description="stdio, http, websocket")
    command: str
    default_args: List[str] = []
    possible_locations: List[str] = []
    env_vars_required: List[str] = []
    auto_detect_enabled: bool = True
    health_check_command: Optional[str] = None
    category: str = Field(..., description="Server category (SAP, Research, etc.)")
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "mcp_server_registry"

class ToolRegistry(Document):
    """Registry of available tools"""
    tool_id: str = Field(..., description="Unique tool identifier")
    name: str
    description: Optional[str] = None
    tool_type: str = Field(..., description="builtin, custom, mcp")
    tool_code: Optional[str] = None
    parameters_schema: Dict[str, Any] = {}
    category: str = Field(..., description="Tool category")
    dependencies: List[str] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "tool_registry"

class AgentConfiguration(Document):
    agent_id: str = Field(..., description="Unique agent identifier")
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    system_prompt_template_id: Optional[str] = None
    system_prompt_variables: Dict[str, Any] = {}
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
    template_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    version: int = 1

    class Settings:
        name = "agent_configurations"
