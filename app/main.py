from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging
from app.config import settings
from app.models.agent import AgentConfiguration
from app.models.execution import AgentExecution
from app.api import agents, executions, websocket
from langfuse import Langfuse

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Langfuse
langfuse = Langfuse(
    public_key=settings.langfuse_public_key,
    secret_key=settings.langfuse_secret_key,
    host=settings.langfuse_host
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    client = AsyncIOMotorClient(settings.mongodb_url)
    await init_beanie(
        database=client[settings.database_name],
        document_models=[AgentConfiguration, AgentExecution]
    )
    logger.info("Service started successfully")
    
    yield
    
    # Shutdown
    client.close()
    await langfuse.flush()
    logger.info("Service shutdown complete")

app = FastAPI(
    title="Agent Orchestration Service",
    description="Dynamic AI agent orchestration with MCP support",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router, prefix=f"/api/{settings.api_version}/agents", tags=["agents"])
app.include_router(executions.router, prefix=f"/api/{settings.api_version}/executions", tags=["executions"])
app.include_router(websocket.router, tags=["websocket"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.environment}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)