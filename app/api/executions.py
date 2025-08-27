# app/api/executions.py
"""
Execution management API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from app.models.execution import AgentExecution

router = APIRouter()

@router.get("/{execution_id}", response_model=Dict[str, Any])
async def get_execution(execution_id: str):
    """Get execution details"""
    execution = await AgentExecution.find_one(
        AgentExecution.execution_id == execution_id
    )
    if not execution:
        raise HTTPException(404, f"Execution {execution_id} not found")
    return execution.dict()

@router.get("/", response_model=Dict[str, Any])
async def list_executions(
    agent_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """List executions with optional filters"""
    query = {}
    if agent_id:
        query["agent_id"] = agent_id
    if status:
        query["status"] = status
    
    executions = await AgentExecution.find(query).skip(skip).limit(limit).to_list()
    total = await AgentExecution.find(query).count()
    
    return {
        "executions": [exec.dict() for exec in executions],
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.delete("/{execution_id}", response_model=Dict[str, str])
async def cancel_execution(execution_id: str):
    """Cancel a running execution"""
    execution = await AgentExecution.find_one(
        AgentExecution.execution_id == execution_id
    )
    if not execution:
        raise HTTPException(404, f"Execution {execution_id} not found")
    
    if execution.status not in ["pending", "running"]:
        raise HTTPException(400, f"Cannot cancel execution in {execution.status} status")
    
    execution.status = "cancelled"
    await execution.save()
    
    return {"message": f"Execution {execution_id} cancelled"}
