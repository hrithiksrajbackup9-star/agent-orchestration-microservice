from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Dict, Any, List, Optional

class ExecutionResult(Document):
    """Store execution results and outputs"""
    result_id: str = Field(..., description="Unique result identifier")
    execution_id: str = Field(..., description="Reference to execution")
    agent_id: str
    result_type: str = Field(..., description="Type of result (report, analysis, etc.)")
    result_data: Dict[str, Any] = Field(..., description="The actual result data")
    file_paths: List[str] = []
    summary: Optional[str] = None
    metrics: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "execution_results"

class AgentExecution(Document):
    execution_id: str
    agent_id: str
    agent_version: int
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    result_id: Optional[str] = None
    status: str = "pending"
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    mcp_servers_used: List[str] = []
    mcp_tools_available: List[str] = []
    system_prompt_used: Optional[str] = None
    configuration_snapshot: Dict[str, Any] = {}
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    langfuse_trace_id: Optional[str] = None
    trace_url: Optional[str] = None
    metadata: Dict[str, Any] = {}
    
    class Settings:
        name = "agent_executions"