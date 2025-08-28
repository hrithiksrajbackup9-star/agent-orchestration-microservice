"""
Master Data Management Service
"""
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.models.master import (
    KTMAgents, KTMTools, KTMMCPs, KTMSystemPrompts, 
    KTMProjects, KTMModelConfigs
)
from app.models.schemas import ModelConfig

logger = logging.getLogger(__name__)

class MasterDataService:
    """Service for managing master data"""
    
    async def create_agent_template(self, data: Dict[str, Any]) -> KTMAgents:
        """Create master agent template"""
        agent = KTMAgents(**data)
        await agent.save()
        logger.info(f"Created agent template: {agent.agent_id}")
        return agent
    
    async def create_tool(self, data: Dict[str, Any]) -> KTMTools:
        """Create master tool"""
        tool = KTMTools(**data)
        await tool.save()
        logger.info(f"Created tool: {tool.tool_id}")
        return tool
    
    async def create_mcp_server(self, data: Dict[str, Any]) -> KTMMCPs:
        """Create master MCP server"""
        mcp = KTMMCPs(**data)
        await mcp.save()
        logger.info(f"Created MCP server: {mcp.mcp_id}")
        return mcp
    
    async def create_system_prompt(self, data: Dict[str, Any]) -> KTMSystemPrompts:
        """Create master system prompt template"""
        prompt = KTMSystemPrompts(**data)
        await prompt.save()
        logger.info(f"Created system prompt: {prompt.prompt_id}")
        return prompt
    
    async def create_model_config(self, data: Dict[str, Any]) -> KTMModelConfigs:
        """Create master model configuration"""
        config = KTMModelConfigs(**data)
        await config.save()
        logger.info(f"Created model config: {config.config_id}")
        return config
    
    # List methods
    async def list_agents(self, category: Optional[str] = None, active_only: bool = True) -> List[KTMAgents]:
        """List agent templates"""
        query = {}
        if active_only:
            query["is_active"] = True
        if category:
            query["category"] = category
        return await KTMAgents.find(query).to_list()
    
    async def list_tools(self, category: Optional[str] = None, active_only: bool = True) -> List[KTMTools]:
        """List tools"""
        query = {}
        if active_only:
            query["is_active"] = True
        if category:
            query["category"] = category
        return await KTMTools.find(query).to_list()
    
    async def list_mcp_servers(self, category: Optional[str] = None, active_only: bool = True) -> List[KTMMCPs]:
        """List MCP servers"""
        query = {}
        if active_only:
            query["is_active"] = True
        if category:
            query["category"] = category
        return await KTMMCPs.find(query).to_list()
    
    async def list_system_prompts(self, category: Optional[str] = None, active_only: bool = True) -> List[KTMSystemPrompts]:
        """List system prompts"""
        query = {}
        if active_only:
            query["is_active"] = True
        if category:
            query["category"] = category
        return await KTMSystemPrompts.find(query).to_list()
    
    async def list_model_configs(self, provider: Optional[str] = None, active_only: bool = True) -> List[KTMModelConfigs]:
        """List model configurations"""
        query = {}
        if active_only:
            query["is_active"] = True
        if provider:
            query["provider"] = provider
        return await KTMModelConfigs.find(query).to_list()
    
    # Get methods
    async def get_agent(self, agent_id: str) -> Optional[KTMAgents]:
        """Get agent template by ID"""
        return await KTMAgents.find_one(KTMAgents.agent_id == agent_id)
    
    async def get_tool(self, tool_id: str) -> Optional[KTMTools]:
        """Get tool by ID"""
        return await KTMTools.find_one(KTMTools.tool_id == tool_id)
    
    async def get_mcp_server(self, mcp_id: str) -> Optional[KTMMCPs]:
        """Get MCP server by ID"""
        return await KTMMCPs.find_one(KTMMCPs.mcp_id == mcp_id)
    
    async def get_system_prompt(self, prompt_id: str) -> Optional[KTMSystemPrompts]:
        """Get system prompt by ID"""
        return await KTMSystemPrompts.find_one(KTMSystemPrompts.prompt_id == prompt_id)
    
    async def get_model_config(self, config_id: str) -> Optional[KTMModelConfigs]:
        """Get model config by ID"""
        return await KTMModelConfigs.find_one(KTMModelConfigs.config_id == config_id)
    
    # Update methods
    async def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> Optional[KTMAgents]:
        """Update agent template"""
        agent = await self.get_agent(agent_id)
        if not agent:
            return None
        
        for key, value in updates.items():
            if hasattr(agent, key):
                setattr(agent, key, value)
        
        agent.updated_at = datetime.utcnow()
        await agent.save()
        logger.info(f"Updated agent template: {agent_id}")
        return agent
    
    # Delete methods
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete agent template (soft delete)"""
        agent = await self.get_agent(agent_id)
        if not agent:
            return False
        
        agent.is_active = False
        agent.updated_at = datetime.utcnow()
        await agent.save()
        logger.info(f"Deleted agent template: {agent_id}")
        return True
    
    # Bulk operations
    async def setup_default_erp_data(self):
        """Setup default ERP master data"""
        
        # Create ERP system prompt
        erp_prompt = {
            "prompt_id": "erp-exception-management-prompt",
            "name": "ERP Exception Management System Prompt",
            "description": "Comprehensive ERP exception analysis prompt",
            "template_content": """You are a specialized ERP Exception Management Expert with comprehensive knowledge of all business process exceptions.

Your responsibility is to perform comprehensive exception detection and analysis across all ERP modules and business processes.

SYSTEM CONTEXT:
- Target System: {{system_name|default('SAP ERP')}}
- Analysis Scope: {{analysis_scope|default('Comprehensive')}}
- Focus Areas: {{focus_areas|default('All Business Processes')}}

Focus on providing actionable insights for ERP administrators and business users.""",
            "variables": {
                "system_name": {"type": "string", "default": "SAP ERP"},
                "analysis_scope": {"type": "string", "default": "Comprehensive"},
                "focus_areas": {"type": "string", "default": "All Business Processes"}
            },
            "category": "ERP"
        }
        
        await self.create_system_prompt(erp_prompt)
        
        # Create model configs
        bedrock_config = {
            "config_id": "bedrock-claude-sonnet-4",
            "name": "Bedrock Claude Sonnet 4",
            "description": "AWS Bedrock Claude Sonnet 4 configuration",
            "provider": "bedrock",
            "model_id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
            "default_temperature": 0.7,
            "default_max_tokens": 4000,
            "client_config": {
                "read_timeout": 300,
                "connect_timeout": 60,
                "retries": {"max_attempts": 2, "mode": "adaptive"}
            },
            "category": "LLM"
        }
        
        await self.create_model_config(bedrock_config)
        
        # Create MCP servers
        sap_mcp = {
            "mcp_id": "sap-abap-adt",
            "name": "SAP ABAP ADT MCP Server",
            "description": "MCP server for SAP ABAP ADT API access",
            "server_type": "stdio",
            "command": "node",
            "possible_locations": [
                r"C:\mcp-abap-abap-adt-api\dist\index.js",
                "~/mcp-abap-abap-adt-api/dist/index.js"
            ],
            "env_vars_required": ["SAP_HOST", "SAP_USER", "SAP_PASSWORD"],
            "auto_detect_enabled": True,
            "category": "SAP"
        }
        
        await self.create_mcp_server(sap_mcp)
        
        # Create tools
        current_time_tool = {
            "tool_id": "current_time",
            "name": "Current Time",
            "description": "Get current date and time",
            "tool_type": "builtin",
            "category": "Utility"
        }
        
        await self.create_tool(current_time_tool)
        
        # Create ERP agent template
        erp_agent = {
            "agent_id": "erp-exception-management",
            "name": "ERP Exception Management Agent",
            "description": "Comprehensive ERP exception detection and analysis",
            "category": "ERP",
            "system_prompt_template": "erp-exception-management-prompt",
            "default_model_config": {
                "provider": "bedrock",
                "model_id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
                "temperature": 0.7,
                "max_tokens": 4000
            },
            "default_mcp_servers": ["sap-abap-adt"],
            "default_tools": [],
            "default_builtin_tools": ["current_time"],
            "capabilities": [
                "Financial Exception Analysis",
                "Procurement Exception Management",
                "Inventory Exception Detection"
            ],
            "tags": ["erp", "exceptions", "sap", "analysis"]
        }
        
        await self.create_agent_template(erp_agent)
        
        logger.info("Default ERP master data setup completed")