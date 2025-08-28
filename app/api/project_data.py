"""
Project-specific Data Management API endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from app.services.project_data_service import ProjectDataService
from app.services.database_manager import db_manager
from app.models.project import (
    KTPAgentInstances, KTPExecutions, KTPResults, 
    KTPTokenUsage, KTPAuditLog
)

router = APIRouter()

async def get_project_service(project_id: str) -> ProjectDataService:
    """Dependency to get project-specific service"""
    project = await db_manager.get_project(project_id)
    if not project:
        raise HTTPException(404, f"Project {project_id} not found")
    
    return ProjectDataService(project_id)

# Agent Instance Management
@router.post("/projects/{project_id}/agent-instances", response_model=Dict[str, Any])
async def create_agent_instance(
    project_id: str, 
    request: Dict[str, Any],
    service: ProjectDataService = Depends(get_project_service)
):
    """Create agent instance for project"""
    try:
        instance = await service.create_agent_instance(request)
        return {
            "message": "Agent instance created successfully",
            "instance_id": instance.instance_id,
            "agent_id": instance.agent_id,
            "name": instance.name
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to create agent instance: {str(e)}")

@router.get("/projects/{project_id}/agent-instances", response_model=Dict[str, Any])
async def list_agent_instances(
    project_id: str,
    agent_id: Optional[str] = None,
    active_only: bool = True,
    service: ProjectDataService = Depends(get_project_service)
):
    """List agent instances for project"""
    instances = await service.list_agent_instances(agent_id=agent_id, active_only=active_only)
    
    return {
        "instances": [
            {
                "instance_id": i.instance_id,
                "agent_id": i.agent_id,
                "name": i.name,
                "description": i.description,
                "is_active": i.is_active,
                "created_at": i.created_at.isoformat(),
                "updated_at": i.updated_at.isoformat()
            }
            for i in instances
        ],
        "total": len(instances)
    }

@router.get("/projects/{project_id}/agent-instances/{instance_id}", response_model=Dict[str, Any])
async def get_agent_instance(
    project_id: str,
    instance_id: str,
    service: ProjectDataService = Depends(get_project_service)
):
    """Get agent instance details"""
    instance = await service.get_agent_instance(instance_id)
    if not instance:
        raise HTTPException(404, f"Agent instance {instance_id} not found")
    
    return {
        "instance_id": instance.instance_id,
        "project_id": instance.project_id,
        "agent_id": instance.agent_id,
        "name": instance.name,
        "description": instance.description,
        "system_prompt": instance.system_prompt,
        "system_prompt_variables": instance.system_prompt_variables,
        "model_config": instance.model_config,
        "mcp_servers": instance.mcp_servers,
        "tools": instance.tools,
        "builtin_tools": instance.builtin_tools,
        "custom_settings": instance.custom_settings,
        "is_active": instance.is_active,
        "created_at": instance.created_at.isoformat(),
        "updated_at": instance.updated_at.isoformat()
    }

# Execution Management
@router.post("/projects/{project_id}/executions", response_model=Dict[str, Any])
async def execute_agent_instance(
    project_id: str,
    request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    service: ProjectDataService = Depends(get_project_service)
):
    """Execute agent instance"""
    try:
        execution = await service.execute_agent_instance(
            instance_id=request["instance_id"],
            input_data=request["input_data"],
            variables=request.get("variables", {}),
            async_execution=request.get("async_execution", True),
            background_tasks=background_tasks
        )
        
        return {
            "execution_id": execution.execution_id,
            "instance_id": execution.instance_id,
            "status": execution.status,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "async_execution": request.get("async_execution", True)
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to execute agent: {str(e)}")

@router.get("/projects/{project_id}/executions", response_model=Dict[str, Any])
async def list_executions(
    project_id: str,
    instance_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    service: ProjectDataService = Depends(get_project_service)
):
    """List executions for project"""
    executions = await service.list_executions(
        instance_id=instance_id,
        agent_id=agent_id,
        status=status,
        limit=limit
    )
    
    return {
        "executions": [
            {
                "execution_id": e.execution_id,
                "instance_id": e.instance_id,
                "agent_id": e.agent_id,
                "status": e.status,
                "started_at": e.started_at.isoformat() if e.started_at else None,
                "completed_at": e.completed_at.isoformat() if e.completed_at else None,
                "duration_ms": e.duration_ms,
                "tokens_used": e.tokens_used,
                "cost_estimate": e.cost_estimate,
                "created_at": e.created_at.isoformat()
            }
            for e in executions
        ],
        "total": len(executions)
    }

@router.get("/projects/{project_id}/executions/{execution_id}", response_model=Dict[str, Any])
async def get_execution(
    project_id: str,
    execution_id: str,
    service: ProjectDataService = Depends(get_project_service)
):
    """Get execution details"""
    execution = await service.get_execution(execution_id)
    if not execution:
        raise HTTPException(404, f"Execution {execution_id} not found")
    
    return {
        "execution_id": execution.execution_id,
        "project_id": execution.project_id,
        "instance_id": execution.instance_id,
        "agent_id": execution.agent_id,
        "input_data": execution.input_data,
        "output_data": execution.output_data,
        "status": execution.status,
        "error_message": execution.error_message,
        "started_at": execution.started_at.isoformat() if execution.started_at else None,
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
        "duration_ms": execution.duration_ms,
        "tokens_used": execution.tokens_used,
        "cost_estimate": execution.cost_estimate,
        "model_used": execution.model_used,
        "mcp_servers_used": execution.mcp_servers_used,
        "tools_used": execution.tools_used,
        "mcp_calls_count": execution.mcp_calls_count,
        "tool_calls_count": execution.tool_calls_count,
        "langfuse_trace_id": execution.langfuse_trace_id,
        "trace_url": execution.trace_url,
        "metadata": execution.metadata,
        "created_at": execution.created_at.isoformat()
    }

@router.get("/projects/{project_id}/executions/{execution_id}/result", response_model=Dict[str, Any])
async def get_execution_result(
    project_id: str,
    execution_id: str,
    service: ProjectDataService = Depends(get_project_service)
):
    """Get execution result"""
    result = await service.get_execution_result(execution_id)
    if not result:
        raise HTTPException(404, f"Result for execution {execution_id} not found")
    
    return {
        "result_id": result.result_id,
        "execution_id": result.execution_id,
        "project_id": result.project_id,
        "agent_id": result.agent_id,
        "result_type": result.result_type,
        "result_data": result.result_data,
        "file_paths": result.file_paths,
        "summary": result.summary,
        "metrics": result.metrics,
        "quality_score": result.quality_score,
        "confidence_score": result.confidence_score,
        "business_impact": result.business_impact,
        "recommendations": result.recommendations,
        "created_at": result.created_at.isoformat()
    }

# Token Usage and Analytics
@router.get("/projects/{project_id}/token-usage", response_model=Dict[str, Any])
async def get_token_usage(
    project_id: str,
    agent_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    service: ProjectDataService = Depends(get_project_service)
):
    """Get token usage analytics"""
    usage_data = await service.get_token_usage_analytics(
        agent_id=agent_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return usage_data

@router.get("/projects/{project_id}/analytics/dashboard", response_model=Dict[str, Any])
async def get_project_dashboard(
    project_id: str,
    service: ProjectDataService = Depends(get_project_service)
):
    """Get project analytics dashboard"""
    dashboard = await service.get_project_dashboard()
    return dashboard

# Audit Log
@router.get("/projects/{project_id}/audit-log", response_model=Dict[str, Any])
async def get_audit_log(
    project_id: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
    service: ProjectDataService = Depends(get_project_service)
):
    """Get audit log for project"""
    logs = await service.get_audit_log(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        limit=limit
    )
    
    return {
        "logs": [
            {
                "log_id": log.log_id,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "action": log.action,
                "user_id": log.user_id,
                "timestamp": log.timestamp.isoformat()
            }
            for log in logs
        ],
        "total": len(logs)
    }