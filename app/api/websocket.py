# app/api/websocket.py
"""
WebSocket endpoints for real-time updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json
import logging
from app.models.execution import AgentExecution

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, execution_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[execution_id] = websocket
    
    def disconnect(self, execution_id: str):
        self.active_connections.pop(execution_id, None)
    
    async def send_update(self, execution_id: str, data: dict):
        if execution_id in self.active_connections:
            websocket = self.active_connections[execution_id]
            try:
                await websocket.send_json(data)
            except Exception as e:
                logger.error(f"Error sending update: {e}")
                self.disconnect(execution_id)

manager = ConnectionManager()

@router.websocket("/ws/execution/{execution_id}")
async def execution_websocket(websocket: WebSocket, execution_id: str):
    """WebSocket for real-time execution updates"""
    await manager.connect(execution_id, websocket)
    
    try:
        while True:
            # Check execution status
            execution = await AgentExecution.find_one(
                AgentExecution.execution_id == execution_id
            )
            
            if execution:
                await websocket.send_json({
                    "execution_id": execution_id,
                    "status": execution.status,
                    "output": execution.output_data,
                    "duration_ms": execution.duration_ms,
                    "error": execution.error_message
                })
                
                if execution.status in ["completed", "failed", "timeout", "cancelled"]:
                    break
            
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        manager.disconnect(execution_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(execution_id)
    finally:
        await websocket.close()
