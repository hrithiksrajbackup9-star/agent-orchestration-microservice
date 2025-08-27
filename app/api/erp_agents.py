# app/api/erp_agents.py
"""
ERP Exception Management API endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
from app.services.erp_exception_agent import ERPExceptionManagementService
from app.models.execution import AgentExecution
from app.models.schemas import ExecuteAgentRequest, AgentResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize the ERP service
erp_service = ERPExceptionManagementService()

@router.get("/status", response_model=Dict[str, Any])
async def get_erp_service_status():
    """Get ERP Exception Management Service status"""
    return erp_service.get_service_status()

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_erp_exceptions(
    background_tasks: BackgroundTasks,
    system_details: Optional[str] = None,
    async_execution: bool = True
):
    """
    Perform comprehensive ERP exception analysis
    
    Args:
        system_details: Optional SAP system connection details
        async_execution: Whether to run analysis asynchronously
    """
    try:
        execution_id = str(uuid.uuid4())
        
        # Create execution record
        execution = AgentExecution(
            execution_id=execution_id,
            agent_id="erp-exception-management",
            agent_version=1,
            input_data={
                "system_details": system_details or "",
                "analysis_type": "comprehensive_erp_exception_analysis"
            },
            status="pending",
            started_at=datetime.utcnow(),
            metadata={
                "service_type": "ERP Exception Management",
                "async_execution": async_execution
            }
        )
        await execution.save()
        
        if async_execution:
            # Run analysis in background
            background_tasks.add_task(
                run_erp_analysis_background,
                execution_id,
                system_details or ""
            )
            
            return {
                "execution_id": execution_id,
                "status": "started",
                "message": "ERP exception analysis started in background",
                "estimated_duration": "5-10 minutes"
            }
        else:
            # Run analysis synchronously
            execution.status = "running"
            await execution.save()
            
            start_time = datetime.utcnow()
            
            try:
                result = await erp_service.perform_comprehensive_exception_analysis(
                    system_details or "",
                    execution_id
                )
                
                end_time = datetime.utcnow()
                duration_ms = int((end_time - start_time).total_seconds() * 1000)
                
                execution.status = "completed"
                execution.completed_at = end_time
                execution.duration_ms = duration_ms
                execution.output_data = result
                await execution.save()
                
                return {
                    "execution_id": execution_id,
                    "status": "completed",
                    "result": result,
                    "duration_ms": duration_ms
                }
                
            except Exception as e:
                end_time = datetime.utcnow()
                duration_ms = int((end_time - start_time).total_seconds() * 1000)
                
                execution.status = "failed"
                execution.completed_at = end_time
                execution.duration_ms = duration_ms
                execution.error_message = str(e)
                await execution.save()
                
                raise HTTPException(500, f"ERP analysis failed: {str(e)}")
                
    except Exception as e:
        logger.error(f"Failed to start ERP exception analysis: {e}")
        raise HTTPException(500, f"Failed to start analysis: {str(e)}")

@router.get("/analyze/{execution_id}", response_model=Dict[str, Any])
async def get_erp_analysis_result(execution_id: str):
    """Get ERP exception analysis result"""
    execution = await AgentExecution.find_one(
        AgentExecution.execution_id == execution_id
    )
    
    if not execution:
        raise HTTPException(404, f"Execution {execution_id} not found")
    
    return {
        "execution_id": execution_id,
        "status": execution.status,
        "started_at": execution.started_at.isoformat() if execution.started_at else None,
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
        "duration_ms": execution.duration_ms,
        "result": execution.output_data,
        "error": execution.error_message
    }

@router.post("/quick-analysis", response_model=Dict[str, Any])
async def quick_erp_analysis(query: str):
    """
    Quick ERP exception analysis for specific queries
    
    Args:
        query: Specific ERP exception query or area to analyze
    """
    try:
        execution_id = str(uuid.uuid4())
        
        # Create execution record
        execution = AgentExecution(
            execution_id=execution_id,
            agent_id="erp-exception-management-quick",
            agent_version=1,
            input_data={
                "query": query,
                "analysis_type": "quick_erp_exception_analysis"
            },
            status="running",
            started_at=datetime.utcnow()
        )
        await execution.save()
        
        start_time = datetime.utcnow()
        
        # For quick analysis, we'll use a simplified approach
        result = {
            "query": query,
            "analysis_type": "quick",
            "recommendations": [
                "Perform comprehensive analysis for detailed insights",
                "Check specific ERP modules mentioned in query",
                "Review system logs for related exceptions"
            ],
            "next_steps": [
                "Run full comprehensive analysis",
                "Check MCP server connections",
                "Review system configuration"
            ]
        }
        
        end_time = datetime.utcnow()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        execution.status = "completed"
        execution.completed_at = end_time
        execution.duration_ms = duration_ms
        execution.output_data = result
        await execution.save()
        
        return {
            "execution_id": execution_id,
            "status": "completed",
            "result": result,
            "duration_ms": duration_ms
        }
        
    except Exception as e:
        logger.error(f"Quick ERP analysis failed: {e}")
        raise HTTPException(500, f"Quick analysis failed: {str(e)}")

async def run_erp_analysis_background(execution_id: str, system_details: str):
    """Background task for running ERP exception analysis"""
    try:
        execution = await AgentExecution.find_one(
            AgentExecution.execution_id == execution_id
        )
        
        if not execution:
            logger.error(f"Execution {execution_id} not found")
            return
        
        execution.status = "running"
        await execution.save()
        
        start_time = datetime.utcnow()
        
        try:
            result = await erp_service.perform_comprehensive_exception_analysis(
                system_details,
                execution_id
            )
            
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            execution.status = "completed"
            execution.completed_at = end_time
            execution.duration_ms = duration_ms
            execution.output_data = result
            await execution.save()
            
            logger.info(f"ERP analysis {execution_id} completed successfully")
            
        except Exception as e:
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            execution.status = "failed"
            execution.completed_at = end_time
            execution.duration_ms = duration_ms
            execution.error_message = str(e)
            execution.error_details = {"background_task_error": True}
            await execution.save()
            
            logger.error(f"ERP analysis {execution_id} failed: {e}")
            
    except Exception as e:
        logger.error(f"Background task error for {execution_id}: {e}")