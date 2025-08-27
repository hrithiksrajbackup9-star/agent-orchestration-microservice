from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Dict, Any, List, Optional

class AgentExecution(Document):
    execution_id: str
    agent_id: str
    agent_version: int
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: str = "pending"
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    mcp_servers_used: List[str] = []
    mcp_tools_available: List[str] = []
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    langfuse_trace_id: Optional[str] = None
    trace_url: Optional[str] = None
    metadata: Dict[str, Any] = {}
    
    class Settings:
        name = "agent_executions"