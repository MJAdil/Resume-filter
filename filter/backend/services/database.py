"""MongoDB database service with async connection management"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)


class DatabaseService:
    """MongoDB database service with connection pooling"""
    
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db: AsyncIOMotorDatabase = None
    
    async def connect(self, uri: str) -> None:
        """
        Connect to MongoDB with connection pooling
        
        Args:
            uri: MongoDB connection URI
        """
        try:
            logger.info("Connecting to MongoDB...")
            
            self.client = AsyncIOMotorClient(
                uri,
                maxPoolSize=50,
                minPoolSize=10,
                serverSelectionTimeoutMS=30000,  # Increased to 30 seconds
                connectTimeoutMS=30000,  # Increased to 30 seconds
                socketTimeoutMS=30000,  # Added socket timeout
                retryWrites=True
            )
            
            # Extract database name from URI or use default
            self.db = self.client.resume_filter
            
            # Verify connection
            await self.client.admin.command('ping')
            
            logger.info("✓ MongoDB connected successfully")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {str(e)}")
            raise
    
    async def disconnect(self) -> None:
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Get the database instance"""
        if self.db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.db
    
    async def create_indexes(self) -> None:
        """Create database indexes for candidates and jobs collections"""
        try:
            logger.info("Creating database indexes...")
            
            # Candidates collection indexes
            await self.db.candidates.create_index("username", unique=True)
            await self.db.candidates.create_index("email")
            await self.db.candidates.create_index("created_at")
            await self.db.candidates.create_index("updated_at")
            
            # Jobs collection indexes
            await self.db.jobs.create_index("job_id", unique=True)
            await self.db.jobs.create_index("company")
            await self.db.jobs.create_index("created_at")
            await self.db.jobs.create_index("jobType")
            
            logger.info("✓ Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """
        Check if database connection is healthy
        
        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False


# Global database service instance
db_service = DatabaseService()
