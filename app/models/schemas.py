from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from datetime import datetime


# -------------------------------------------------------------------
# ENUMS
# -------------------------------------------------------------------
class ModelProvider(str, Enum):
    BEDROCK = "bedrock"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    PERPLEXITY = "perplexity"


class MCPServerType(str, Enum):
    STDIO = "stdio"
    HTTP = "http"
    WEBSOCKET = "websocket"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


# -------------------------------------------------------------------
# ERP EXCEPTION MANAGEMENT SCHEMAS
# -------------------------------------------------------------------
class ERPExceptionCategory(str, Enum):
    FINANCIAL = "FINANCIAL"
    PROCUREMENT = "PROCUREMENT"
    INVENTORY = "INVENTORY"
    ORDER_FULFILLMENT = "ORDER_FULFILLMENT"
    PRODUCTION = "PRODUCTION"
    INVOICE_MATCHING = "INVOICE_MATCHING"
    HR = "HR"
    COMPLIANCE = "COMPLIANCE"
    LOGISTICS = "LOGISTICS"
    CUSTOMER_MANAGEMENT = "CUSTOMER_MANAGEMENT"
    SYSTEM_DATA = "SYSTEM_DATA"
    QUALITY_MANAGEMENT = "QUALITY_MANAGEMENT"
    PROJECT_MANAGEMENT = "PROJECT_MANAGEMENT"
    MAINTENANCE = "MAINTENANCE"


class ERPExceptionSeverity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ERPAnalysisRequest(BaseModel):
    system_details: Optional[str] = None
    analysis_type: str = "comprehensive"
    focus_areas: List[ERPExceptionCategory] = []
    async_execution: bool = True


class ERPQuickAnalysisRequest(BaseModel):
    query: str
    focus_category: Optional[ERPExceptionCategory] = None


# -------------------------------------------------------------------
# CONFIGURATION MODELS
# -------------------------------------------------------------------
class MCPServerConfig(BaseModel):
    server_type: MCPServerType = MCPServerType.STDIO
    server_name: str
    command: str
    args: List[str] = []
    env_vars: Dict[str, str] = {}
    auto_detect_path: bool = True
    possible_locations: List[str] = []
    enabled: bool = True
    timeout: int = 30


class ToolConfig(BaseModel):
    tool_name: str
    tool_type: str
    parameters: Dict[str, Any] = {}
    code: Optional[str] = None
    enabled: bool = True


class ModelConfig(BaseModel):
    provider: ModelProvider
    model_id: str
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: Optional[float] = None
    api_key_env: Optional[str] = None
    client_config: Dict[str, Any] = {}


# -------------------------------------------------------------------
# AGENT DEFINITIONS
# -------------------------------------------------------------------
class AgentConfig(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    model: Optional[ModelConfig] = None
    tools: List[ToolConfig] = []
    mcp_servers: List[MCPServerConfig] = []
    enabled: bool = True


# -------------------------------------------------------------------
# REQUEST / RESPONSE SCHEMAS
# -------------------------------------------------------------------


class AgentResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    execution_id: Optional[str] = None
    status: ExecutionStatus = ExecutionStatus.SUCCESS
    timestamp: datetime = datetime.utcnow()


# -------------------------------------------------------------------
# EXECUTION TRACKING
# -------------------------------------------------------------------
class ExecutionRequest(BaseModel):
    execution_id: str
    agent_id: str
    params: Dict[str, Any] = {}
    created_at: datetime = datetime.utcnow()
    status: ExecutionStatus = ExecutionStatus.PENDING


class ExecutionUpdate(BaseModel):
    execution_id: str
    status: ExecutionStatus
    progress: Optional[float] = None  # 0–100
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    updated_at: datetime = datetime.utcnow()


# -------------------------------------------------------------------
# WEBSOCKET EVENT SCHEMAS
# -------------------------------------------------------------------
class WebSocketEvent(BaseModel):
    event: str
    execution_id: str
    payload: Union[ExecutionUpdate, Dict[str, Any]]


# Additional schemas for request/response models
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
from datetime import datetime

class ExecuteAgentRequest(BaseModel):
    agent_id: Optional[str] = None
    input_data: Dict[str, Any]
    system_prompt_override: Optional[str] = None
    model_override: Optional[ModelConfig] = None
    mcp_servers_override: Optional[List[MCPServerConfig]] = None
    tools_override: Optional[List[ToolConfig]] = None
    timeout_override: Optional[int] = None
    async_execution: bool = False
    stream_response: bool = False
    include_trace: bool = True
    metadata: Optional[Dict[str, Any]] = {}
    
    @validator('input_data')
    def validate_input_data(cls, v):
        if not v:
            raise ValueError("input_data cannot be empty")
        return v

class AgentResponse(BaseModel):
    execution_id: str
    agent_id: str
    status: str
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    trace_url: Optional[str] = None

class WorkflowRequest(BaseModel):
    workflow_name: str
    agent_sequence: List[str]
    initial_input: Dict[str, Any]
    parallel_execution: bool = False
    metadata: Optional[Dict[str, Any]] = {}
