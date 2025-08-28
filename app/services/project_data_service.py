"""
Project-specific Data Management Service
"""
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import BackgroundTasks

from app.services.database_manager import db_manager
from app.services.master_data_service import MasterDataService
from app.services.multi_tenant_agent_service import MultiTenantAgentService
from app.models.project import (
    KTPAgentInstances, KTPExecutions, KTPResults, 
    KTPTokenUsage, KTPAuditLog
)

logger = logging.getLogger(__name__)

class ProjectDataService:
    """Service for managing project-specific data"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.master_service = MasterDataService()
        self.agent_service = MultiTenantAgentService()
    
    async def _get_project_db(self):
        """Get project database"""
        return await db_manager.get_project_database(self.project_id)
    
    async def _log_audit(self, entity_type: str, entity_id: str, action: str, 
                        old_values: Dict[str, Any] = None, new_values: Dict[str, Any] = None,
                        user_id: str = None):
        """Log audit entry"""
        try:
            await db_manager.get_project_database(self.project_id)  # Ensure DB is initialized
            
            audit_log = KTPAuditLog(
                log_id=str(uuid.uuid4()),
                project_id=self.project_id,
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                old_values=old_values,
                new_values=new_values,
                user_id=user_id
            )
            await audit_log.save()
        except Exception as e:
            logger.error(f"Failed to log audit entry: {e}")
    
    # Agent Instance Management
    async def create_agent_instance(self, data: Dict[str, Any]) -> KTPAgentInstances:
        """Create agent instance from master template"""
        await self._get_project_db()  # Ensure DB is initialized
        
        # Get master agent template
        master_agent = await self.master_service.get_agent(data["agent_id"])
        if not master_agent:
            raise ValueError(f"Master agent {data['agent_id']} not found")
        
        # Create instance
        instance = KTPAgentInstances(
            instance_id=data.get("instance_id", str(uuid.uuid4())),
            project_id=self.project_id,
            agent_id=data["agent_id"],
            name=data.get("name", master_agent.name),
            description=data.get("description", master_agent.description),
            system_prompt_variables=data.get("system_prompt_variables", {}),
            model_config=data.get("model_config", master_agent.default_model_config.dict()),
            mcp_servers=data.get("mcp_servers", []),
            tools=data.get("tools", []),
            builtin_tools=data.get("builtin_tools", master_agent.default_builtin_tools),
            custom_settings=data.get("custom_settings", {}),
            created_by=data.get("created_by")
        )
        
        await instance.save()
        
        # Log audit
        await self._log_audit("agent_instance", instance.instance_id, "create", 
                             new_values=instance.dict(), user_id=data.get("created_by"))
        
        logger.info(f"Created agent instance: {instance.instance_id} for project: {self.project_id}")
        return instance
    
    async def list_agent_instances(self, agent_id: str = None, active_only: bool = True) -> List[KTPAgentInstances]:
        """List agent instances for project"""
        await self._get_project_db()
        
        query = {"project_id": self.project_id}
        if agent_id:
            query["agent_id"] = agent_id
        if active_only:
            query["is_active"] = True
        
        return await KTPAgentInstances.find(query).to_list()
    
    async def get_agent_instance(self, instance_id: str) -> Optional[KTPAgentInstances]:
        """Get agent instance by ID"""
        await self._get_project_db()
        return await KTPAgentInstances.find_one(
            KTPAgentInstances.instance_id == instance_id,
            KTPAgentInstances.project_id == self.project_id
        )
    
    async def update_agent_instance(self, instance_id: str, updates: Dict[str, Any], user_id: str = None) -> Optional[KTPAgentInstances]:
        """Update agent instance"""
        instance = await self.get_agent_instance(instance_id)
        if not instance:
            return None
        
        old_values = instance.dict()
        
        for key, value in updates.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        instance.updated_at = datetime.utcnow()
        await instance.save()
        
        # Log audit
        await self._log_audit("agent_instance", instance_id, "update", 
                             old_values=old_values, new_values=instance.dict(), user_id=user_id)
        
        return instance
    
    # Execution Management
    async def execute_agent_instance(
        self, 
        instance_id: str, 
        input_data: Dict[str, Any],
        variables: Dict[str, Any] = None,
        async_execution: bool = True,
        background_tasks: BackgroundTasks = None
    ) -> KTPExecutions:
        """Execute agent instance"""
        await self._get_project_db()
        
        # Get agent instance
        instance = await self.get_agent_instance(instance_id)
        if not instance:
            raise ValueError(f"Agent instance {instance_id} not found")
        
        # Create execution record
        execution = KTPExecutions(
            execution_id=str(uuid.uuid4()),
            project_id=self.project_id,
            instance_id=instance_id,
            agent_id=instance.agent_id,
            input_data=input_data,
            status="pending",
            started_at=datetime.utcnow(),
            metadata={"variables": variables or {}, "async_execution": async_execution},
            configuration_snapshot=instance.dict()
        )
        
        await execution.save()
        
        # Log audit
        await self._log_audit("execution", execution.execution_id, "create", 
                             new_values={"execution_id": execution.execution_id, "status": "pending"})
        
        if async_execution and background_tasks:
            # Execute in background
            background_tasks.add_task(
                self._execute_agent_background, execution.execution_id, instance, input_data, variables
            )
        else:
            # Execute synchronously
            await self._execute_agent_sync(execution, instance, input_data, variables)
        
        return execution
    
    async def _execute_agent_sync(
        self, 
        execution: KTPExecutions, 
        instance: KTPAgentInstances,
        input_data: Dict[str, Any],
        variables: Dict[str, Any] = None
    ):
        """Execute agent synchronously"""
        try:
            execution.status = "running"
            await execution.save()
            
            # Execute using multi-tenant agent service
            result = await self.agent_service.execute_agent_instance(
                project_id=self.project_id,
                instance=instance,
                input_data=input_data,
                variables=variables
            )
            
            # Save result
            result_id = await self._save_execution_result(execution.execution_id, result)
            
            # Update execution
            execution.status = "completed"
            execution.completed_at = datetime.utcnow()
            execution.duration_ms = int(
                (execution.completed_at - execution.started_at).total_seconds() * 1000
            )
            execution.output_data = {"result_summary": "Execution completed successfully"}
            execution.tokens_used = result.get("tokens_used", 0)
            execution.cost_estimate = result.get("cost_estimate", 0.0)
            execution.model_used = result.get("model_used")
            execution.mcp_servers_used = result.get("mcp_servers_used", [])
            execution.tools_used = result.get("tools_used", [])
            
            await execution.save()
            
            # Log token usage
            await self._log_token_usage(execution, result)
            
            # Log audit
            await self._log_audit("execution", execution.execution_id, "complete", 
                                 new_values={"status": "completed", "duration_ms": execution.duration_ms})
            
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            if execution.started_at:
                execution.duration_ms = int(
                    (execution.completed_at - execution.started_at).total_seconds() * 1000
                )
            await execution.save()
            
            # Log audit
            await self._log_audit("execution", execution.execution_id, "fail", 
                                 new_values={"status": "failed", "error": str(e)})
            raise
    
    async def _execute_agent_background(
        self, 
        execution_id: str, 
        instance: KTPAgentInstances,
        input_data: Dict[str, Any],
        variables: Dict[str, Any] = None
    ):
        """Execute agent in background"""
        try:
            execution = await KTPExecutions.find_one(KTPExecutions.execution_id == execution_id)
            if not execution:
                logger.error(f"Execution {execution_id} not found")
                return
            
            await self._execute_agent_sync(execution, instance, input_data, variables)
            
        except Exception as e:
            logger.error(f"Background execution failed: {e}")
    
    async def _save_execution_result(self, execution_id: str, result_data: Dict[str, Any]) -> str:
        """Save execution result"""
        result_id = str(uuid.uuid4())
        
        # Determine result type
        result_type = "general"
        if "exception_analysis" in str(result_data):
            result_type = "erp_exception_analysis"
        elif "report" in str(result_data):
            result_type = "report"
        
        # Create result
        result = KTPResults(
            result_id=result_id,
            execution_id=execution_id,
            project_id=self.project_id,
            agent_id=result_data.get("agent_id", "unknown"),
            result_type=result_type,
            result_data=result_data,
            summary=self._create_result_summary(result_data),
            metrics=self._extract_metrics(result_data),
            business_impact=result_data.get("business_impact", {}),
            recommendations=result_data.get("recommendations", [])
        )
        
        await result.save()
        return result_id
    
    async def _log_token_usage(self, execution: KTPExecutions, result_data: Dict[str, Any]):
        """Log token usage"""
        if not result_data.get("tokens_used"):
            return
        
        usage = KTPTokenUsage(
            usage_id=str(uuid.uuid4()),
            project_id=self.project_id,
            execution_id=execution.execution_id,
            agent_id=execution.agent_id,
            model_provider=result_data.get("model_provider", "unknown"),
            model_id=result_data.get("model_id", "unknown"),
            input_tokens=result_data.get("input_tokens", 0),
            output_tokens=result_data.get("output_tokens", 0),
            total_tokens=result_data.get("tokens_used", 0),
            cost_per_input_token=result_data.get("cost_per_input_token"),
            cost_per_output_token=result_data.get("cost_per_output_token"),
            total_cost=result_data.get("cost_estimate", 0.0),
            usage_type="execution",
            context={"execution_id": execution.execution_id}
        )
        
        await usage.save()
    
    def _create_result_summary(self, result_data: Dict[str, Any]) -> str:
        """Create result summary"""
        response = result_data.get("response", "")
        if len(response) > 500:
            return response[:500] + "..."
        return response
    
    def _extract_metrics(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics from result"""
        metrics = {}
        response = result_data.get("response", "")
        metrics["response_length"] = len(response)
        
        # Add more metric extraction logic here
        return metrics
    
    # Query Methods
    async def list_executions(
        self, 
        instance_id: str = None,
        agent_id: str = None,
        status: str = None,
        limit: int = 100
    ) -> List[KTPExecutions]:
        """List executions for project"""
        await self._get_project_db()
        
        query = {"project_id": self.project_id}
        if instance_id:
            query["instance_id"] = instance_id
        if agent_id:
            query["agent_id"] = agent_id
        if status:
            query["status"] = status
        
        return await KTPExecutions.find(query).limit(limit).sort("-started_at").to_list()
    
    async def get_execution(self, execution_id: str) -> Optional[KTPExecutions]:
        """Get execution by ID"""
        await self._get_project_db()
        return await KTPExecutions.find_one(
            KTPExecutions.execution_id == execution_id,
            KTPExecutions.project_id == self.project_id
        )
    
    async def get_execution_result(self, execution_id: str) -> Optional[KTPResults]:
        """Get execution result"""
        await self._get_project_db()
        return await KTPResults.find_one(
            KTPResults.execution_id == execution_id,
            KTPResults.project_id == self.project_id
        )
    
    # Analytics Methods
    async def get_token_usage_analytics(
        self, 
        agent_id: str = None,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """Get token usage analytics"""
        await self._get_project_db()
        
        query = {"project_id": self.project_id}
        if agent_id:
            query["agent_id"] = agent_id
        
        # Add date filtering if provided
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = datetime.fromisoformat(start_date)
            if end_date:
                date_filter["$lte"] = datetime.fromisoformat(end_date)
            query["timestamp"] = date_filter
        
        usage_records = await KTPTokenUsage.find(query).to_list()
        
        # Calculate analytics
        total_tokens = sum(record.total_tokens for record in usage_records)
        total_cost = sum(record.total_cost or 0 for record in usage_records)
        
        # Group by model
        by_model = {}
        for record in usage_records:
            model_key = f"{record.model_provider}:{record.model_id}"
            if model_key not in by_model:
                by_model[model_key] = {"tokens": 0, "cost": 0, "calls": 0}
            by_model[model_key]["tokens"] += record.total_tokens
            by_model[model_key]["cost"] += record.total_cost or 0
            by_model[model_key]["calls"] += 1
        
        return {
            "project_id": self.project_id,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "total_calls": len(usage_records),
            "by_model": by_model,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            }
        }
    
    async def get_project_dashboard(self) -> Dict[str, Any]:
        """Get project dashboard analytics"""
        await self._get_project_db()
        
        # Get counts
        instances_count = len(await self.list_agent_instances())
        executions_count = len(await self.list_executions(limit=10000))
        
        # Get recent executions
        recent_executions = await self.list_executions(limit=10)
        
        # Get token usage for last 30 days
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
        token_usage = await self.get_token_usage_analytics(start_date=thirty_days_ago)
        
        # Get execution status distribution
        status_counts = {}
        all_executions = await self.list_executions(limit=10000)
        for execution in all_executions:
            status = execution.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "project_id": self.project_id,
            "summary": {
                "agent_instances": instances_count,
                "total_executions": executions_count,
                "tokens_used_30d": token_usage["total_tokens"],
                "cost_30d": token_usage["total_cost"]
            },
            "execution_status": status_counts,
            "recent_executions": [
                {
                    "execution_id": e.execution_id,
                    "agent_id": e.agent_id,
                    "status": e.status,
                    "started_at": e.started_at.isoformat() if e.started_at else None
                }
                for e in recent_executions
            ],
            "token_usage_30d": token_usage
        }
    
    async def get_audit_log(
        self, 
        entity_type: str = None,
        entity_id: str = None,
        action: str = None,
        limit: int = 100
    ) -> List[KTPAuditLog]:
        """Get audit log"""
        await self._get_project_db()
        
        query = {"project_id": self.project_id}
        if entity_type:
            query["entity_type"] = entity_type
        if entity_id:
            query["entity_id"] = entity_id
        if action:
            query["action"] = action
        
        return await KTPAuditLog.find(query).limit(limit).sort("-timestamp").to_list()