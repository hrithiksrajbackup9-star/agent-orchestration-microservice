"""
Multi-tenant Database Manager
"""
import logging
from typing import Dict, Any, Optional, List
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from app.config import settings
from app.models.master import (
    KTMAgents, KTMTools, KTMMCPs, KTMSystemPrompts, 
    KTMProjects, KTMModelConfigs
)
from app.models.project import (
    KTPAgentInstances, KTPExecutions, KTPResults, 
    KTPTokenUsage, KTPAuditLog
)

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages master and project databases"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.master_db: Optional[AsyncIOMotorDatabase] = None
        self.project_dbs: Dict[str, AsyncIOMotorDatabase] = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize database connections"""
        if self._initialized:
            return
        
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        self.master_db = self.client[settings.master_database_name]
        
        # Initialize master database
        await init_beanie(
            database=self.master_db,
            document_models=[
                KTMAgents, KTMTools, KTMMCPs, KTMSystemPrompts,
                KTMProjects, KTMModelConfigs
            ]
        )
        
        logger.info(f"Master database initialized: {settings.master_database_name}")
        self._initialized = True
    
    async def get_project_database(self, project_id: str) -> AsyncIOMotorDatabase:
        """Get or create project database"""
        if project_id in self.project_dbs:
            return self.project_dbs[project_id]
        
        # Check if project exists in master
        project = await KTMProjects.find_one(KTMProjects.project_id == project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found in master database")
        
        # Get project database
        db_name = project.database_name
        project_db = self.client[db_name]
        
        # Initialize project database
        await init_beanie(
            database=project_db,
            document_models=[
                KTPAgentInstances, KTPExecutions, KTPResults,
                KTPTokenUsage, KTPAuditLog
            ]
        )
        
        self.project_dbs[project_id] = project_db
        logger.info(f"Project database initialized: {db_name} for project {project_id}")
        
        return project_db
    
    async def create_project(
        self, 
        project_id: str, 
        project_name: str, 
        customer_name: str,
        description: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> KTMProjects:
        """Create new project and database"""
        
        # Check if project already exists
        existing = await KTMProjects.find_one(KTMProjects.project_id == project_id)
        if existing:
            raise ValueError(f"Project {project_id} already exists")
        
        # Create project record
        db_name = f"{settings.project_database_prefix}{project_id}"
        project = KTMProjects(
            project_id=project_id,
            project_name=project_name,
            customer_name=customer_name,
            description=description,
            database_name=db_name,
            created_by=created_by
        )
        
        await project.save()
        
        # Initialize project database
        await self.get_project_database(project_id)
        
        logger.info(f"Created project: {project_id} with database: {db_name}")
        return project
    
    async def list_projects(self, active_only: bool = True) -> List[KTMProjects]:
        """List all projects"""
        query = {}
        if active_only:
            query["status"] = "active"
        
        return await KTMProjects.find(query).to_list()
    
    async def get_project(self, project_id: str) -> Optional[KTMProjects]:
        """Get project by ID"""
        return await KTMProjects.find_one(KTMProjects.project_id == project_id)
    
    async def close(self):
        """Close database connections"""
        if self.client:
            self.client.close()
            self._initialized = False
            logger.info("Database connections closed")

# Global database manager instance
db_manager = DatabaseManager()