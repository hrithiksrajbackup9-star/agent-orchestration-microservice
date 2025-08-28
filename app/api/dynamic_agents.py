"""
Dynamic Agent API endpoints - Database-driven agent management
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from app.services.dynamic_agent_service import DynamicAgentService
from app.services.template_service import TemplateService
from app.models.agent import AgentConfiguration, AgentTemplate
from app.models.execution import AgentExecution, ExecutionResult

router = APIRouter()

# Initialize services
agent_service = DynamicAgentService()
template_service = TemplateService()

@router.post("/execute/{agent_id}", response_model=Dict[str, Any])
async def execute_agent(
    agent_id: str,
    request: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Execute agent by ID with database configuration"""
    
    input_data = request.get("input_data", {})
    variables = request.get("variables", {})
    async_execution = request.get("async_execution", False)
    
    try:
        execution = await agent_service.execute_agent_by_id(
            agent_id=agent_id,
            input_data=input_data,
            variables=variables,
            async_execution=async_execution
        )
        
        return {
            "execution_id": execution.execution_id,
            "status": execution.status,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "async_execution": async_execution
        }
        
    except Exception as e:
        raise HTTPException(500, f"Agent execution failed: {str(e)}")

@router.get("/execution/{execution_id}/result", response_model=Dict[str, Any])
async def get_execution_result(execution_id: str):
    """Get execution result"""
    
    result = await agent_service.get_execution_result(execution_id)
    if not result:
        raise HTTPException(404, "Execution result not found")
    
    return {
        "result_id": result.result_id,
        "execution_id": result.execution_id,
        "agent_id": result.agent_id,
        "result_type": result.result_type,
        "result_data": result.result_data,
        "summary": result.summary,
        "metrics": result.metrics,
        "created_at": result.created_at.isoformat()
    }

@router.get("/execution/{execution_id}/status", response_model=Dict[str, Any])
async def get_execution_status(execution_id: str):
    """Get execution status"""
    
    execution = await AgentExecution.find_one(
        AgentExecution.execution_id == execution_id
    )
    
    if not execution:
        raise HTTPException(404, "Execution not found")
    
    return {
        "execution_id": execution.execution_id,
        "agent_id": execution.agent_id,
        "status": execution.status,
        "started_at": execution.started_at.isoformat() if execution.started_at else None,
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
        "duration_ms": execution.duration_ms,
        "error_message": execution.error_message,
        "result_id": execution.result_id
    }

@router.get("/executions", response_model=Dict[str, Any])
async def list_executions(
    agent_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100
):
    """List executions with filters"""
    
    executions = await agent_service.list_executions(
        agent_id=agent_id,
        status=status,
        limit=limit
    )
    
    return {
        "executions": [
            {
                "execution_id": exec.execution_id,
                "agent_id": exec.agent_id,
                "status": exec.status,
                "started_at": exec.started_at.isoformat() if exec.started_at else None,
                "completed_at": exec.completed_at.isoformat() if exec.completed_at else None,
                "duration_ms": exec.duration_ms,
                "result_id": exec.result_id
            }
            for exec in executions
        ],
        "total": len(executions)
    }

@router.post("/agents/from-template", response_model=Dict[str, Any])
async def create_agent_from_template(request: Dict[str, Any]):
    """Create agent configuration from template"""
    
    template_id = request.get("template_id")
    agent_id = request.get("agent_id")
    variables = request.get("variables", {})
    overrides = request.get("overrides", {})
    
    if not template_id or not agent_id:
        raise HTTPException(400, "template_id and agent_id are required")
    
    try:
        config = await template_service.create_agent_from_template(
            template_id=template_id,
            agent_id=agent_id,
            variables=variables,
            overrides=overrides
        )
        
        # Save agent configuration
        agent_config = AgentConfiguration(**config)
        await agent_config.save()
        
        return {
            "message": "Agent created from template successfully",
            "agent_id": agent_id,
            "template_id": template_id
        }
        
    except Exception as e:
        raise HTTPException(500, f"Failed to create agent from template: {str(e)}")

@router.get("/templates", response_model=Dict[str, Any])
async def list_agent_templates(category: Optional[str] = None):
    """List available agent templates"""
    
    templates = await template_service.list_templates(category=category)
    
    return {
        "templates": [
            {
                "template_id": template.template_id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "capabilities": template.capabilities,
                "tags": template.tags
            }
            for template in templates
        ]
    }

@router.get("/templates/prompts", response_model=Dict[str, Any])
async def list_prompt_templates(category: Optional[str] = None):
    """List available system prompt templates"""
    
    templates = await template_service.list_system_prompt_templates(category=category)
    
    return {
        "templates": [
            {
                "template_id": template.template_id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "variables": template.variables
            }
            for template in templates
        ]
    }

@router.get("/registry/mcp-servers", response_model=Dict[str, Any])
async def list_mcp_servers(category: Optional[str] = None):
    """List available MCP servers from registry"""
    
    servers = await template_service.list_mcp_servers(category=category)
    
    return {
        "servers": [
            {
                "server_id": server.server_id,
                "name": server.name,
                "description": server.description,
                "server_type": server.server_type,
                "category": server.category,
                "command": server.command
            }
            for server in servers
        ]
    }

@router.get("/registry/tools", response_model=Dict[str, Any])
async def list_tools(category: Optional[str] = None):
    """List available tools from registry"""
    
    tools = await template_service.list_tools(category=category)
    
    return {
        "tools": [
            {
                "tool_id": tool.tool_id,
                "name": tool.name,
                "description": tool.description,
                "tool_type": tool.tool_type,
                "category": tool.category
            }
            for tool in tools
        ]
    }