"""
Multi-tenant Agent Execution Service
"""
import logging
import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime

from app.services.agent_builder import DynamicAgentBuilder
from app.services.master_data_service import MasterDataService
from app.models.project import KTPAgentInstances
from app.models.master import KTMSystemPrompts
from jinja2 import Template, Environment, BaseLoader

logger = logging.getLogger(__name__)

class MultiTenantAgentService:
    """Service for executing agents in multi-tenant environment"""
    
    def __init__(self):
        self.agent_builder = DynamicAgentBuilder()
        self.master_service = MasterDataService()
        self.jinja_env = Environment(loader=BaseLoader())
    
    async def execute_agent_instance(
        self,
        project_id: str,
        instance: KTPAgentInstances,
        input_data: Dict[str, Any],
        variables: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute agent instance with project-specific configuration"""
        
        try:
            # Get master agent template
            master_agent = await self.master_service.get_agent(instance.agent_id)
            if not master_agent:
                raise ValueError(f"Master agent {instance.agent_id} not found")
            
            # Resolve system prompt
            system_prompt = await self._resolve_system_prompt(
                master_agent, instance, variables or {}
            )
            
            # Build agent configuration
            agent_config = self._build_agent_config(master_agent, instance, system_prompt)
            
            # Build and execute agent
            agent = await self.agent_builder.build_agent(agent_config)
            
            # Execute agent
            prompt = input_data.get("prompt", json.dumps(input_data))
            
            # Execute with timeout
            timeout = instance.custom_settings.get("timeout", 600)
            async with asyncio.timeout(timeout):
                result = await asyncio.to_thread(agent, prompt)
            
            # Process result
            if isinstance(result, str):
                response_data = {"response": result}
            else:
                response_data = {"response": str(result)}
            
            # Add execution metadata
            response_data.update({
                "project_id": project_id,
                "instance_id": instance.instance_id,
                "agent_id": instance.agent_id,
                "execution_timestamp": datetime.utcnow().isoformat(),
                "model_used": agent_config.get("model_id"),
                "tokens_used": self._estimate_tokens(prompt, result),
                "cost_estimate": self._estimate_cost(prompt, result, agent_config.get("model_id"))
            })
            
            return response_data
            
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            raise
    
    async def _resolve_system_prompt(
        self,
        master_agent,
        instance: KTPAgentInstances,
        variables: Dict[str, Any]
    ) -> str:
        """Resolve system prompt from template"""
        
        # Use instance-specific prompt if available
        if instance.system_prompt:
            return instance.system_prompt
        
        # Get system prompt template
        prompt_template = await self.master_service.get_system_prompt(
            master_agent.system_prompt_template
        )
        
        if not prompt_template:
            return "You are a helpful AI assistant."
        
        # Merge variables: template defaults < instance variables < execution variables
        merged_variables = {}
        
        # Start with template defaults
        for var_name, var_config in prompt_template.variables.items():
            merged_variables[var_name] = var_config.get('default', '')
        
        # Override with instance variables
        merged_variables.update(instance.system_prompt_variables)
        
        # Override with execution variables
        merged_variables.update(variables)
        
        # Render template
        jinja_template = self.jinja_env.from_string(prompt_template.template_content)
        return jinja_template.render(**merged_variables)
    
    def _build_agent_config(
        self,
        master_agent,
        instance: KTPAgentInstances,
        system_prompt: str
    ) -> Dict[str, Any]:
        """Build agent configuration from master template and instance"""
        
        # Start with master agent defaults
        config = {
            "agent_id": instance.instance_id,
            "name": instance.name,
            "system_prompt": system_prompt,
            "agent_model_config": instance.model_config or master_agent.default_model_config.dict(),
            "mcp_servers": instance.mcp_servers or [],
            "tools": instance.tools or [],
            "builtin_tools": instance.builtin_tools or master_agent.default_builtin_tools,
            "timeout": instance.custom_settings.get("timeout", 600),
            "chunking_enabled": instance.custom_settings.get("chunking_enabled", False),
            "chunk_size": instance.custom_settings.get("chunk_size", 1000)
        }
        
        return config
    
    def _estimate_tokens(self, prompt: str, result: Any) -> int:
        """Estimate token usage (rough approximation)"""
        # Simple estimation: ~4 characters per token
        prompt_tokens = len(str(prompt)) // 4
        result_tokens = len(str(result)) // 4
        return prompt_tokens + result_tokens
    
    def _estimate_cost(self, prompt: str, result: Any, model_id: str) -> float:
        """Estimate execution cost"""
        tokens = self._estimate_tokens(prompt, result)
        
        # Simple cost estimation (adjust based on actual model pricing)
        cost_per_1k_tokens = {
            "us.anthropic.claude-sonnet-4-20250514-v1:0": 0.003,  # Example pricing
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002
        }
        
        rate = cost_per_1k_tokens.get(model_id, 0.002)  # Default rate
        return (tokens / 1000) * rate