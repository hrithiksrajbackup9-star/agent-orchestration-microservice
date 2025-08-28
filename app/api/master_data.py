"""
Master Data Management API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from app.services.master_data_service import MasterDataService
from app.services.database_manager import db_manager
from app.models.master import (
    KTMAgents, KTMTools, KTMMCPs, KTMSystemPrompts, 
    KTMProjects, KTMModelConfigs
)

router = APIRouter()
master_service = MasterDataService()

# Project Management Endpoints
@router.post("/projects", response_model=Dict[str, Any])
async def create_project(request: Dict[str, Any]):
    """Create new customer project"""
    try:
        project = await db_manager.create_project(
            project_id=request["project_id"],
            project_name=request["project_name"],
            customer_name=request["customer_name"],
            description=request.get("description"),
            created_by=request.get("created_by")
        )
        
        return {
            "message": "Project created successfully",
            "project": {
                "project_id": project.project_id,
                "project_name": project.project_name,
                "customer_name": project.customer_name,
                "database_name": project.database_name,
                "status": project.status,
                "created_at": project.created_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Failed to create project: {str(e)}")

@router.get("/projects", response_model=Dict[str, Any])
async def list_projects(active_only: bool = True):
    """List all projects"""
    projects = await db_manager.list_projects(active_only=active_only)
    
    return {
        "projects": [
            {
                "project_id": p.project_id,
                "project_name": p.project_name,
                "customer_name": p.customer_name,
                "database_name": p.database_name,
                "status": p.status,
                "created_at": p.created_at.isoformat()
            }
            for p in projects
        ],
        "total": len(projects)
    }

@router.get("/projects/{project_id}", response_model=Dict[str, Any])
async def get_project(project_id: str):
    """Get project details"""
    project = await db_manager.get_project(project_id)
    if not project:
        raise HTTPException(404, f"Project {project_id} not found")
    
    return {
        "project_id": project.project_id,
        "project_name": project.project_name,
        "customer_name": project.customer_name,
        "database_name": project.database_name,
        "status": project.status,
        "settings": project.settings,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat()
    }

# Agent Template Management
@router.post("/agents", response_model=Dict[str, Any])
async def create_agent_template(request: Dict[str, Any]):
    """Create master agent template"""
    try:
        agent = await master_service.create_agent_template(request)
        return {
            "message": "Agent template created successfully",
            "agent_id": agent.agent_id,
            "name": agent.name,
            "category": agent.category
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to create agent template: {str(e)}")

@router.get("/agents", response_model=Dict[str, Any])
async def list_agent_templates(category: Optional[str] = None, active_only: bool = True):
    """List agent templates"""
    agents = await master_service.list_agents(category=category, active_only=active_only)
    
    return {
        "agents": [
            {
                "agent_id": a.agent_id,
                "name": a.name,
                "description": a.description,
                "category": a.category,
                "capabilities": a.capabilities,
                "tags": a.tags,
                "version": a.version,
                "is_active": a.is_active,
                "created_at": a.created_at.isoformat()
            }
            for a in agents
        ],
        "total": len(agents)
    }

@router.get("/agents/{agent_id}", response_model=Dict[str, Any])
async def get_agent_template(agent_id: str):
    """Get agent template details"""
    agent = await master_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(404, f"Agent template {agent_id} not found")
    
    return {
        "agent_id": agent.agent_id,
        "name": agent.name,
        "description": agent.description,
        "category": agent.category,
        "system_prompt_template": agent.system_prompt_template,
        "default_model_config": agent.default_model_config,
        "default_mcp_servers": agent.default_mcp_servers,
        "default_tools": agent.default_tools,
        "default_builtin_tools": agent.default_builtin_tools,
        "template_variables": agent.template_variables,
        "capabilities": agent.capabilities,
        "tags": agent.tags,
        "version": agent.version,
        "is_active": agent.is_active,
        "created_at": agent.created_at.isoformat(),
        "updated_at": agent.updated_at.isoformat()
    }

@router.put("/agents/{agent_id}", response_model=Dict[str, Any])
async def update_agent_template(agent_id: str, updates: Dict[str, Any]):
    """Update agent template"""
    agent = await master_service.update_agent(agent_id, updates)
    if not agent:
        raise HTTPException(404, f"Agent template {agent_id} not found")
    
    return {
        "message": "Agent template updated successfully",
        "agent_id": agent.agent_id,
        "version": agent.version
    }

@router.delete("/agents/{agent_id}", response_model=Dict[str, Any])
async def delete_agent_template(agent_id: str):
    """Delete agent template (soft delete)"""
    success = await master_service.delete_agent(agent_id)
    if not success:
        raise HTTPException(404, f"Agent template {agent_id} not found")
    
    return {"message": f"Agent template {agent_id} deleted successfully"}

# System Prompt Management
@router.post("/system-prompts", response_model=Dict[str, Any])
async def create_system_prompt(request: Dict[str, Any]):
    """Create system prompt template"""
    try:
        prompt = await master_service.create_system_prompt(request)
        return {
            "message": "System prompt created successfully",
            "prompt_id": prompt.prompt_id,
            "name": prompt.name
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to create system prompt: {str(e)}")

@router.get("/system-prompts", response_model=Dict[str, Any])
async def list_system_prompts(category: Optional[str] = None, active_only: bool = True):
    """List system prompt templates"""
    prompts = await master_service.list_system_prompts(category=category, active_only=active_only)
    
    return {
        "prompts": [
            {
                "prompt_id": p.prompt_id,
                "name": p.name,
                "description": p.description,
                "category": p.category,
                "variables": p.variables,
                "version": p.version,
                "is_active": p.is_active,
                "created_at": p.created_at.isoformat()
            }
            for p in prompts
        ],
        "total": len(prompts)
    }

@router.get("/system-prompts/{prompt_id}", response_model=Dict[str, Any])
async def get_system_prompt(prompt_id: str):
    """Get system prompt template"""
    prompt = await master_service.get_system_prompt(prompt_id)
    if not prompt:
        raise HTTPException(404, f"System prompt {prompt_id} not found")
    
    return {
        "prompt_id": prompt.prompt_id,
        "name": prompt.name,
        "description": prompt.description,
        "template_content": prompt.template_content,
        "variables": prompt.variables,
        "category": prompt.category,
        "version": prompt.version,
        "is_active": prompt.is_active,
        "created_at": prompt.created_at.isoformat()
    }

# MCP Server Management
@router.post("/mcp-servers", response_model=Dict[str, Any])
async def create_mcp_server(request: Dict[str, Any]):
    """Create MCP server configuration"""
    try:
        mcp = await master_service.create_mcp_server(request)
        return {
            "message": "MCP server created successfully",
            "mcp_id": mcp.mcp_id,
            "name": mcp.name
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to create MCP server: {str(e)}")

@router.get("/mcp-servers", response_model=Dict[str, Any])
async def list_mcp_servers(category: Optional[str] = None, active_only: bool = True):
    """List MCP servers"""
    servers = await master_service.list_mcp_servers(category=category, active_only=active_only)
    
    return {
        "servers": [
            {
                "mcp_id": s.mcp_id,
                "name": s.name,
                "description": s.description,
                "server_type": s.server_type,
                "command": s.command,
                "category": s.category,
                "version": s.version,
                "is_active": s.is_active,
                "created_at": s.created_at.isoformat()
            }
            for s in servers
        ],
        "total": len(servers)
    }

# Tool Management
@router.post("/tools", response_model=Dict[str, Any])
async def create_tool(request: Dict[str, Any]):
    """Create tool configuration"""
    try:
        tool = await master_service.create_tool(request)
        return {
            "message": "Tool created successfully",
            "tool_id": tool.tool_id,
            "name": tool.name
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to create tool: {str(e)}")

@router.get("/tools", response_model=Dict[str, Any])
async def list_tools(category: Optional[str] = None, active_only: bool = True):
    """List tools"""
    tools = await master_service.list_tools(category=category, active_only=active_only)
    
    return {
        "tools": [
            {
                "tool_id": t.tool_id,
                "name": t.name,
                "description": t.description,
                "tool_type": t.tool_type,
                "category": t.category,
                "version": t.version,
                "is_active": t.is_active,
                "created_at": t.created_at.isoformat()
            }
            for t in tools
        ],
        "total": len(tools)
    }

# Model Configuration Management
@router.post("/model-configs", response_model=Dict[str, Any])
async def create_model_config(request: Dict[str, Any]):
    """Create model configuration"""
    try:
        config = await master_service.create_model_config(request)
        return {
            "message": "Model configuration created successfully",
            "config_id": config.config_id,
            "name": config.name
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to create model config: {str(e)}")

@router.get("/model-configs", response_model=Dict[str, Any])
async def list_model_configs(provider: Optional[str] = None, active_only: bool = True):
    """List model configurations"""
    configs = await master_service.list_model_configs(provider=provider, active_only=active_only)
    
    return {
        "configs": [
            {
                "config_id": c.config_id,
                "name": c.name,
                "description": c.description,
                "provider": c.provider,
                "model_id": c.model_id,
                "default_temperature": c.default_temperature,
                "default_max_tokens": c.default_max_tokens,
                "category": c.category,
                "is_active": c.is_active,
                "created_at": c.created_at.isoformat()
            }
            for c in configs
        ],
        "total": len(configs)
    }

# Bulk Setup Operations
@router.post("/setup/erp-defaults", response_model=Dict[str, Any])
async def setup_erp_defaults():
    """Setup default ERP master data"""
    try:
        await master_service.setup_default_erp_data()
        return {
            "message": "ERP default master data setup completed successfully",
            "components_created": [
                "ERP system prompt template",
                "Bedrock model configuration",
                "SAP MCP server configuration",
                "Built-in tools",
                "ERP agent template"
            ]
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to setup ERP defaults: {str(e)}")

@router.get("/health", response_model=Dict[str, Any])
async def master_data_health():
    """Health check for master data service"""
    try:
        # Check master database connection
        projects_count = len(await db_manager.list_projects())
        agents_count = len(await master_service.list_agents())
        
        return {
            "status": "healthy",
            "master_database": settings.master_database_name,
            "projects_count": projects_count,
            "agents_count": agents_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(500, f"Health check failed: {str(e)}")