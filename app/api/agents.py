# app/api/agents.py
"""
Agent management API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from datetime import datetime
from app.models.agent import AgentConfiguration
from app.models.schemas import ExecuteAgentRequest, AgentResponse
from app.services.agent_builder import DynamicAgentBuilder

router = APIRouter()
orchestrator = DynamicAgentBuilder()

@router.post("/register", response_model=Dict[str, Any])
async def register_agent(config: AgentConfiguration):
    """Register a new agent with full configuration"""
    
    # Check if agent exists
    existing = await AgentConfiguration.find_one(
        AgentConfiguration.agent_id == config.agent_id
    )
    
    if existing:
        config.version = existing.version + 1
        config.updated_at = datetime.utcnow()
    
    await config.save()
    
    return {
        "message": "Agent registered successfully",
        "agent_id": config.agent_id,
        "version": config.version
    }

@router.get("/{agent_id}/config", response_model=Dict[str, Any])
async def get_agent_config(agent_id: str):
    """Get agent configuration"""
    config = await AgentConfiguration.find_one(
        AgentConfiguration.agent_id == agent_id
    )
    if not config:
        raise HTTPException(404, f"Agent {agent_id} not found")
    return config.dict()

@router.put("/{agent_id}/config", response_model=Dict[str, Any])
async def update_agent_config(agent_id: str, updates: Dict[str, Any]):
    """Update agent configuration dynamically"""
    config = await AgentConfiguration.find_one(
        AgentConfiguration.agent_id == agent_id
    )
    if not config:
        raise HTTPException(404, f"Agent {agent_id} not found")
    
    for key, value in updates.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    config.version += 1
    config.updated_at = datetime.utcnow()
    await config.save()
    
    return {"message": "Configuration updated", "version": config.version}

@router.delete("/{agent_id}", response_model=Dict[str, str])
async def delete_agent(agent_id: str):
    """Delete an agent configuration"""
    config = await AgentConfiguration.find_one(
        AgentConfiguration.agent_id == agent_id
    )
    if not config:
        raise HTTPException(404, f"Agent {agent_id} not found")
    
    await config.delete()
    return {"message": f"Agent {agent_id} deleted successfully"}

@router.get("/", response_model=Dict[str, Any])
async def list_agents(skip: int = 0, limit: int = 100, tags: List[str] = None):
    """List all agents with optional filtering"""
    query = {}
    if tags:
        query["tags"] = {"$in": tags}
    
    agents = await AgentConfiguration.find(query).skip(skip).limit(limit).to_list()
    total = await AgentConfiguration.find(query).count()
    
    return {
        "agents": [
            {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "description": agent.description,
                "capabilities": agent.capabilities,
                "tags": agent.tags,
                "created_at": agent.created_at.isoformat()
            }
            for agent in agents
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.post("/{agent_id}/execute", response_model=Dict[str, Any])
async def execute_agent(agent_id: str, request: ExecuteAgentRequest):
    """Execute an agent with dynamic configuration"""
    request.agent_id = agent_id
    execution = await orchestrator.execute_agent(request)
    return execution.dict()