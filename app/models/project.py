"""
Project Database Models - Customer-specific data
"""
from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Dict, Any, List, Optional

class KTPAgentInstances(Document):
    """Project Agent Instances - kt_p_agent_instances"""
    instance_id: str = Field(..., description="Unique instance identifier")
    project_id: str = Field(..., description="Project identifier")
    agent_id: str = Field(..., description="Reference to master agent")
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    system_prompt_variables: Dict[str, Any] = {}
    model_config: Dict[str, Any] = {}
    mcp_servers: List[Dict[str, Any]] = []
    tools: List[Dict[str, Any]] = []
    builtin_tools: List[str] = []
    custom_settings: Dict[str, Any] = {}
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    
    class Settings:
        name = "kt_p_agent_instances"

class KTPExecutions(Document):
    """Project Executions - kt_p_executions"""
    execution_id: str = Field(..., description="Unique execution identifier")
    project_id: str = Field(..., description="Project identifier")
    instance_id: str = Field(..., description="Agent instance identifier")
    agent_id: str = Field(..., description="Master agent identifier")
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: str = "pending"  # pending, running, completed, failed, cancelled
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    
    # Execution tracking
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    
    # Resource usage tracking
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    model_used: Optional[str] = None
    
    # MCP and tools tracking
    mcp_servers_used: List[str] = []
    tools_used: List[str] = []
    mcp_calls_count: int = 0
    tool_calls_count: int = 0
    
    # Tracing
    langfuse_trace_id: Optional[str] = None
    trace_url: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = {}
    configuration_snapshot: Dict[str, Any] = {}
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    
    class Settings:
        name = "kt_p_executions"

class KTPResults(Document):
    """Project Execution Results - kt_p_results"""
    result_id: str = Field(..., description="Unique result identifier")
    execution_id: str = Field(..., description="Reference to execution")
    project_id: str = Field(..., description="Project identifier")
    agent_id: str = Field(..., description="Master agent identifier")
    result_type: str = Field(..., description="Type of result")
    result_data: Dict[str, Any] = Field(..., description="The actual result data")
    file_paths: List[str] = []
    summary: Optional[str] = None
    
    # Analysis metrics
    metrics: Dict[str, Any] = {}
    quality_score: Optional[float] = None
    confidence_score: Optional[float] = None
    
    # Business impact
    business_impact: Dict[str, Any] = {}
    recommendations: List[str] = []
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "kt_p_results"

class KTPTokenUsage(Document):
    """Project Token Usage Tracking - kt_p_token_usage"""
    usage_id: str = Field(..., description="Unique usage identifier")
    project_id: str = Field(..., description="Project identifier")
    execution_id: str = Field(..., description="Reference to execution")
    agent_id: str = Field(..., description="Master agent identifier")
    
    # Token details
    model_provider: str
    model_id: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    
    # Cost tracking
    cost_per_input_token: Optional[float] = None
    cost_per_output_token: Optional[float] = None
    total_cost: Optional[float] = None
    
    # Usage context
    usage_type: str = Field(..., description="execution, mcp_call, tool_call")
    context: Dict[str, Any] = {}
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "kt_p_token_usage"

class KTPAuditLog(Document):
    """Project Audit Log - kt_p_audit_log"""
    log_id: str = Field(..., description="Unique log identifier")
    project_id: str = Field(..., description="Project identifier")
    entity_type: str = Field(..., description="agent, execution, result, etc.")
    entity_id: str = Field(..., description="ID of the entity")
    action: str = Field(..., description="create, update, delete, execute")
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "kt_p_audit_log"