"""
Template Service for managing dynamic agent configurations
"""
import logging
from typing import Dict, Any, List, Optional
from jinja2 import Template, Environment, BaseLoader
from app.models.agent import AgentTemplate, SystemPromptTemplate, MCPServerRegistry, ToolRegistry
from app.models.schemas import ModelConfig, MCPServerConfig, ToolConfig

logger = logging.getLogger(__name__)

class TemplateService:
    """Service for managing agent templates and dynamic configuration"""
    
    def __init__(self):
        self.jinja_env = Environment(loader=BaseLoader())
    
    async def get_agent_template(self, template_id: str) -> Optional[AgentTemplate]:
        """Get agent template by ID"""
        return await AgentTemplate.find_one(
            AgentTemplate.template_id == template_id,
            AgentTemplate.is_active == True
        )
    
    async def get_system_prompt_template(self, template_id: str) -> Optional[SystemPromptTemplate]:
        """Get system prompt template by ID"""
        return await SystemPromptTemplate.find_one(
            SystemPromptTemplate.template_id == template_id,
            SystemPromptTemplate.is_active == True
        )
    
    async def render_system_prompt(self, template_id: str, variables: Dict[str, Any]) -> str:
        """Render system prompt template with variables"""
        template = await self.get_system_prompt_template(template_id)
        if not template:
            raise ValueError(f"System prompt template {template_id} not found")
        
        # Merge with default variables
        merged_vars = {}
        for var_name, var_config in template.variables.items():
            merged_vars[var_name] = variables.get(var_name, var_config.get('default', ''))
        
        # Render template
        jinja_template = self.jinja_env.from_string(template.template_content)
        return jinja_template.render(**merged_vars)
    
    async def get_mcp_servers_from_registry(self, server_ids: List[str]) -> List[MCPServerConfig]:
        """Get MCP server configurations from registry"""
        servers = []
        for server_id in server_ids:
            registry_entry = await MCPServerRegistry.find_one(
                MCPServerRegistry.server_id == server_id,
                MCPServerRegistry.is_active == True
            )
            if registry_entry:
                server_config = MCPServerConfig(
                    server_type=registry_entry.server_type,
                    server_name=registry_entry.name,
                    command=registry_entry.command,
                    args=registry_entry.default_args,
                    auto_detect_path=registry_entry.auto_detect_enabled,
                    possible_locations=registry_entry.possible_locations,
                    enabled=True
                )
                servers.append(server_config)
        return servers
    
    async def get_tools_from_registry(self, tool_ids: List[str]) -> List[ToolConfig]:
        """Get tool configurations from registry"""
        tools = []
        for tool_id in tool_ids:
            registry_entry = await ToolRegistry.find_one(
                ToolRegistry.tool_id == tool_id,
                ToolRegistry.is_active == True
            )
            if registry_entry:
                tool_config = ToolConfig(
                    tool_name=registry_entry.name,
                    tool_type=registry_entry.tool_type,
                    parameters=registry_entry.parameters_schema,
                    code=registry_entry.tool_code,
                    enabled=True
                )
                tools.append(tool_config)
        return tools
    
    async def create_agent_from_template(
        self, 
        template_id: str, 
        agent_id: str,
        variables: Dict[str, Any] = None,
        overrides: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create agent configuration from template"""
        template = await self.get_agent_template(template_id)
        if not template:
            raise ValueError(f"Agent template {template_id} not found")
        
        variables = variables or {}
        overrides = overrides or {}
        
        # Render system prompt if template uses one
        system_prompt = None
        if template.system_prompt_template:
            # Extract template ID from system_prompt_template field
            prompt_template_id = template.system_prompt_template
            system_prompt = await self.render_system_prompt(prompt_template_id, variables)
        else:
            # Use direct template rendering
            jinja_template = self.jinja_env.from_string(template.system_prompt_template)
            system_prompt = jinja_template.render(**variables)
        
        # Build configuration
        config = {
            "agent_id": agent_id,
            "name": overrides.get("name", template.name),
            "description": overrides.get("description", template.description),
            "system_prompt": system_prompt,
            "agent_model_config": overrides.get("model_config", template.default_model_config.dict()),
            "mcp_servers": overrides.get("mcp_servers", [server.dict() for server in template.default_mcp_servers]),
            "tools": overrides.get("tools", [tool.dict() for tool in template.default_tools]),
            "builtin_tools": overrides.get("builtin_tools", template.default_builtin_tools),
            "capabilities": template.capabilities,
            "tags": template.tags,
            "template_id": template_id,
            "metadata": {
                "created_from_template": template_id,
                "template_variables": variables,
                **template.template_variables
            }
        }
        
        return config
    
    async def list_templates(self, category: Optional[str] = None) -> List[AgentTemplate]:
        """List available agent templates"""
        query = {"is_active": True}
        if category:
            query["category"] = category
        
        return await AgentTemplate.find(query).to_list()
    
    async def list_system_prompt_templates(self, category: Optional[str] = None) -> List[SystemPromptTemplate]:
        """List available system prompt templates"""
        query = {"is_active": True}
        if category:
            query["category"] = category
        
        return await SystemPromptTemplate.find(query).to_list()
    
    async def list_mcp_servers(self, category: Optional[str] = None) -> List[MCPServerRegistry]:
        """List available MCP servers"""
        query = {"is_active": True}
        if category:
            query["category"] = category
        
        return await MCPServerRegistry.find(query).to_list()
    
    async def list_tools(self, category: Optional[str] = None) -> List[ToolRegistry]:
        """List available tools"""
        query = {"is_active": True}
        if category:
            query["category"] = category
        
        return await ToolRegistry.find(query).to_list()