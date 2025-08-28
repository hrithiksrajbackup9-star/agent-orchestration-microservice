"""
Master Database Models - Shared across all projects
"""
from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.models.schemas import ModelConfig, MCPServerConfig, ToolConfig

class KTMAgents(Document):
    """Master Agent Templates - kt_m_agents"""
    agent_id: str = Field(..., description="Unique agent identifier")
    name: str
    description: Optional[str] = None
    category: str = Field(..., description="Agent category (ERP, Finance, etc.)")
    system_prompt_template: str = Field(..., description="System prompt with placeholders")
    default_model_config: ModelConfig
    default_mcp_servers: List[str] = []  # References to kt_m_mcps
    default_tools: List[str] = []  # References to kt_m_tools
    default_builtin_tools: List[str] = []
    template_variables: Dict[str, Any] = Field(default_factory=dict)
    capabilities: List[str] = []
    tags: List[str] = []
    version: str = "1.0.0"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    
    class Settings:
        name = "kt_m_agents"

class KTMTools(Document):
    """Master Tools Registry - kt_m_tools"""
    tool_id: str = Field(..., description="Unique tool identifier")
    name: str
    description: Optional[str] = None
    tool_type: str = Field(..., description="builtin, custom, mcp")
    tool_code: Optional[str] = None
    parameters_schema: Dict[str, Any] = {}
    category: str = Field(..., description="Tool category")
    dependencies: List[str] = []
    version: str = "1.0.0"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "kt_m_tools"

class KTMMCPs(Document):
    """Master MCP Servers Registry - kt_m_mcps"""
    mcp_id: str = Field(..., description="Unique MCP server identifier")
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
    version: str = "1.0.0"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "kt_m_mcps"

class KTMSystemPrompts(Document):
    """Master System Prompt Templates - kt_m_system_prompts"""
    prompt_id: str = Field(..., description="Unique prompt identifier")
    name: str
    description: Optional[str] = None
    template_content: str = Field(..., description="Prompt template with {{variable}} placeholders")
    variables: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    category: str = Field(..., description="Prompt category")
    version: str = "1.0.0"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "kt_m_system_prompts"

class KTMProjects(Document):
    """Master Projects Registry - kt_m_projects"""
    project_id: str = Field(..., description="Unique project identifier")
    project_name: str
    customer_name: str
    description: Optional[str] = None
    database_name: str = Field(..., description="Project-specific database name")
    status: str = Field(default="active", description="active, inactive, archived")
    settings: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    
    class Settings:
        name = "kt_m_projects"

class KTMModelConfigs(Document):
    """Master Model Configurations - kt_m_model_configs"""
    config_id: str = Field(..., description="Unique config identifier")
    name: str
    description: Optional[str] = None
    provider: str = Field(..., description="bedrock, openai, anthropic, perplexity")
    model_id: str
    default_temperature: float = 0.7
    default_max_tokens: int = 2000
    default_top_p: Optional[float] = None
    client_config: Dict[str, Any] = {}
    cost_per_token: Optional[float] = None
    category: str = Field(..., description="Model category")
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "kt_m_model_configs"