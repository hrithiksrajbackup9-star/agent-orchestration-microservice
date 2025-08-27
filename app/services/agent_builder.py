import os
import logging
from typing import Dict, Any, List, Optional, Callable
from strands import Agent, tool, models
from strands.models import BedrockModel
from strands_tools import current_time
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from app.models.schemas import ModelConfig, MCPServerConfig, ToolConfig, ModelProvider, MCPServerType

logger = logging.getLogger(__name__)

class DynamicAgentBuilder:
    def __init__(self):
        self.mcp_connections: Dict[str, Any] = {}
        self.custom_tools: Dict[str, Callable] = {}
        
    def create_model(self, config: ModelConfig) -> models:
        if config.provider == ModelProvider.BEDROCK:
            return BedrockModel(
                model_id=config.model_id,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                client_config=config.client_config
            )
        elif config.provider == ModelProvider.OPENAI:
            api_key = os.getenv(config.api_key_env or "OPENAI_API_KEY")
            return OpenAIModel(
                model=config.model_id,
                api_key=api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
        elif config.provider == ModelProvider.ANTHROPIC:
            api_key = os.getenv(config.api_key_env or "ANTHROPIC_API_KEY")
            return AnthropicModel(
                model=config.model_id,
                api_key=api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
        elif config.provider == ModelProvider.PERPLEXITY:
            api_key = os.getenv(config.api_key_env or "PERPLEXITY_API_KEY")
            return self._create_perplexity_model(config, api_key)
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")
    
    def _create_perplexity_model(self, config: ModelConfig, api_key: str):
        from openai import OpenAI
        
        class PerplexityModel(model):
            def __init__(self, model_id, api_key, **kwargs):
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.perplexity.ai"
                )
                self.model_id = model_id
                self.kwargs = kwargs
                
            def __call__(self, prompt: str) -> str:
                response = self.client.chat.completions.create(
                    model=self.model_id,
                    messages=[{"role": "user", "content": prompt}],
                    **self.kwargs
                )
                return response.choices[0].message.content
        
        return PerplexityModel(
            model_id=config.model_id,
            api_key=api_key,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
    
    async def setup_mcp_servers(self, mcp_configs: List[MCPServerConfig]) -> List[Any]:
        all_tools = []
        
        for mcp_config in mcp_configs:
            if not mcp_config.enabled:
                continue
                
            try:
                if mcp_config.auto_detect_path:
                    server_path = self._find_mcp_server(mcp_config)
                    if server_path:
                        mcp_config.args[0] = server_path
                
                if mcp_config.server_type == MCPServerType.STDIO:
                    def create_connection():
                        return stdio_client(
                            StdioServerParameters(
                                command=mcp_config.command,
                                args=mcp_config.args,
                                env={**os.environ, **mcp_config.env_vars}
                            )
                        )
                    
                    mcp_client = MCPClient(create_connection)
                    
                    with mcp_client as client:
                        tools = client.list_tools_sync()
                        all_tools.extend(tools if tools else [])
                    
                    self.mcp_connections[mcp_config.server_name] = mcp_client
                    
            except Exception as e:
                logger.error(f"Failed to setup MCP server {mcp_config.server_name}: {e}")
                
        return all_tools
    
    def _find_mcp_server(self, config: MCPServerConfig) -> Optional[str]:
        for location in config.possible_locations:
            expanded_path = os.path.expanduser(location)
            if os.path.exists(expanded_path):
                return expanded_path
        return None
    
    def create_custom_tool(self, tool_config: ToolConfig) -> Callable:
        if tool_config.code:
            namespace = {}
            exec(tool_config.code, namespace)
            
            for name, obj in namespace.items():
                if callable(obj) and hasattr(obj, '__tool__'):
                    return obj
        
        @tool
        def custom_tool(**kwargs):
            return f"Executing {tool_config.tool_name} with params: {kwargs}"
        
        return custom_tool
    
    def get_builtin_tools(self, tool_names: List[str]) -> List[Callable]:
        builtin_tools = {
            "current_time": current_time,
        }
        
        tools = []
        for name in tool_names:
            if name in builtin_tools:
                tools.append(builtin_tools[name])
        
        return tools
    
    async def build_agent(self, config) -> Agent:
        model = self.create_model(config.model_config)
        mcp_tools = await self.setup_mcp_servers(config.mcp_servers)
        
        custom_tools = []
        for tool_config in config.tools:
            if tool_config.enabled and tool_config.tool_type == "custom":
                custom_tools.append(self.create_custom_tool(tool_config))
        
        builtin_tools = self.get_builtin_tools(config.builtin_tools)
        all_tools = builtin_tools + mcp_tools + custom_tools
        
        agent = Agent(
            model=model,
            tools=all_tools,
            system_prompt=config.system_prompt
        )
        
        return agent