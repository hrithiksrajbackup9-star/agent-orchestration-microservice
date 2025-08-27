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
class ExecuteAgentRequest(BaseModel):
    agent_id: str
    params: Dict[str, Any] = {}


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
