# app/services/agent_builder.py
"""
Dynamic agent builder service
"""
import os
import logging
from typing import Dict, Any, List, Optional, Callable
from strands import Agent, tool, models
from strands.models import BedrockModel
from strands_tools import current_time
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from app.models.agent import ModelConfig, MCPServerConfig, ToolConfig

logger = logging.getLogger(__name__)

class DynamicAgentBuilder:
    def __init__(self):
        self.mcp_connections: Dict[str, Any] = {}
        self.custom_tools: Dict[str, Callable] = {}
        
    def create_model(self, config: ModelConfig) -> models:
        """Create appropriate model based on provider"""
        
        if config.provider == "bedrock":
            return BedrockModel(
                model_id=config.model_id,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                client_config=config.client_config if config.client_config else {}
            )
            
        # elif config.provider == "openai":
        #     api_key = os.getenv(config.api_key_env or "OPENAI_API_KEY")
        #     return OpenAIModel(
        #         model=config.model_id,
        #         api_key=api_key,
        #         temperature=config.temperature,
        #         max_tokens=config.max_tokens,
        #         **(config.client_config if config.client_config else {})
        #     )
            
        # elif config.provider == ModelProvider.ANTHROPIC:
        #     api_key = os.getenv(config.api_key_env or "ANTHROPIC_API_KEY")
        #     return AnthropicModel(
        #         model=config.model_id,
        #         api_key=api_key,
        #         temperature=config.temperature,
        #         max_tokens=config.max_tokens,
        #         **(config.client_config if config.client_config else {})
        #     )
            
        elif config.provider == "perplexity":
            api_key = os.getenv(config.api_key_env or "PERPLEXITY_API_KEY")
            return self._create_perplexity_model(config, api_key)
            
        else:
            raise ValueError(f"Unsupported model provider: {config.provider}")
    
    def _create_perplexity_model(self, config: ModelConfig, api_key: str):
        """Create Perplexity model (using OpenAI-compatible interface)"""
        try:
            from openai import OpenAI
        except ImportError:
            logger.error("OpenAI package not installed for Perplexity model")
            raise ImportError("Please install openai package: pip install openai")
        
        class PerplexityModel(models):
            def __init__(self, model_id, api_key, **kwargs):
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.perplexity.ai"
                )
                self.model_id = model_id
                self.kwargs = kwargs
                
            def __call__(self, prompt: str) -> str:
                try:
                    response = self.client.chat.completions.create(
                        model=self.model_id,
                        messages=[{"role": "user", "content": prompt}],
                        **self.kwargs
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    logger.error(f"Perplexity API call failed: {str(e)}")
                    raise
        
        return PerplexityModel(
            model_id=config.model_id,
            api_key=api_key,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
    
    async def setup_mcp_servers(self, mcp_configs: List[MCPServerConfig]) -> List[Any]:
        """Setup MCP servers and return available tools"""
        all_tools = []
        
        for mcp_config in mcp_configs:
            if not mcp_config.enabled:
                continue
                
            try:
                # Auto-detect server path if needed
                if mcp_config.auto_detect_path:
                    server_path = self._find_mcp_server(mcp_config)
                    if not server_path:
                        logger.warning(f"MCP server {mcp_config.server_name} not found at any location")
                        continue
                    mcp_config.args[0] = server_path
                    logger.info(f"Found MCP server {mcp_config.server_name} at: {server_path}")
                
                # Create MCP connection
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
                    
                    # Get available tools
                    with mcp_client as client:
                        tools = client.list_tools_sync()
                        all_tools.extend(tools if tools else [])
                        logger.info(f"Connected to MCP server {mcp_config.server_name}: {len(tools) if tools else 0} tools available")
                    
                    # Store connection for later use
                    self.mcp_connections[mcp_config.server_name] = mcp_client
                    
            except Exception as e:
                logger.error(f"Failed to setup MCP server {mcp_config.server_name}: {str(e)}")
                continue
                
        return all_tools
    
    def _find_mcp_server(self, config: MCPServerConfig) -> Optional[str]:
        """Auto-detect MCP server path"""
        for location in config.possible_locations:
            expanded_path = os.path.expanduser(location)
            if os.path.exists(expanded_path):
                return expanded_path
        return None
    
    def create_custom_tool(self, tool_config: ToolConfig) -> Callable:
        """Create custom tool from configuration"""
        if tool_config.code:
            try:
                # Dynamic tool creation from code
                namespace = {'tool': tool}  # Make tool decorator available
                exec(tool_config.code, namespace)
                
                # Find the tool function
                for name, obj in namespace.items():
                    if callable(obj) and hasattr(obj, '__tool__'):
                        logger.info(f"Created custom tool: {tool_config.tool_name}")
                        return obj
            except Exception as e:
                logger.error(f"Failed to create custom tool {tool_config.tool_name}: {str(e)}")
                    
        # Return a placeholder tool if creation fails
        @tool
        def custom_tool(**kwargs):
            """Custom tool placeholder"""
            return f"Executing {tool_config.tool_name} with params: {kwargs}"
        
        return custom_tool
    
    def get_builtin_tools(self, tool_names: List[str]) -> List[Callable]:
        """Get built-in Strands tools"""
        builtin_tools = {
            "current_time": current_time,
            # Add more built-in tools as needed
        }
        
        tools = []
        for name in tool_names:
            if name in builtin_tools:
                tools.append(builtin_tools[name])
                logger.info(f"Added built-in tool: {name}")
            else:
                logger.warning(f"Built-in tool not found: {name}")
        
        return tools
    
    async def build_agent(self, config) -> Agent:
        """Build a complete Strands agent from configuration"""
        
        try:

            print("BUILDING AGENT")
            # Handle both field names: model_config or agent_model_config
            model_config = None
            if hasattr(config, 'agent_model_config'):
                model_config = config.agent_model_config
            elif hasattr(config, 'model_config'):
                model_config = config.model_config
            else:
                raise ValueError("No model configuration found in agent config")
            
            # Create model
            logger.info(f"Creating model with provider: {model_config.provider}")
            model = self.create_model(model_config)
            
            # Setup MCP servers and get tools
            logger.info("Setting up MCP servers...")
            mcp_tools = []
            if hasattr(config, 'mcp_servers') and config.mcp_servers:
                mcp_tools = await self.setup_mcp_servers(config.mcp_servers)
            
            # Get custom tools
            logger.info("Creating custom tools...")
            custom_tools = []
            if hasattr(config, 'tools') and config.tools:
                for tool_config in config.tools:
                    if tool_config.enabled and tool_config.tool_type == "custom":
                        custom_tool = self.create_custom_tool(tool_config)
                        if custom_tool:
                            custom_tools.append(custom_tool)
            
            # Get built-in tools
            logger.info("Adding built-in tools...")
            builtin_tools = []
            if hasattr(config, 'builtin_tools') and config.builtin_tools:
                builtin_tools = self.get_builtin_tools(config.builtin_tools)
            
            # Combine all tools
            all_tools = builtin_tools + mcp_tools + custom_tools
            logger.info(f"Total tools available: {len(all_tools)}")
            
            # Create agent
            logger.info("Creating agent...")
            agent = Agent(
                model=model,
                tools=all_tools if all_tools else [],
                system_prompt=config.system_prompt if hasattr(config, 'system_prompt') else "You are a helpful assistant"
            )
            
            logger.info("Agent successfully built")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to build agent: {str(e)}", exc_info=True)
            raise