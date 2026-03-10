"""Test script to verify MongoDB connection and setup"""
import asyncio
import logging
from dotenv import load_dotenv
from config import get_settings, log_configuration
from services.database import db_service
from utils.logging import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


async def test_database_connection():
    """Test database connection and index creation"""
    try:
        # Load settings
        settings = get_settings()
        log_configuration(settings)
        
        # Connect to database
        logger.info("Testing database connection...")
        await db_service.connect(settings.mongodb_uri)
        
        # Create indexes
        await db_service.create_indexes()
        
        # Test health check
        is_healthy = await db_service.health_check()
        if is_healthy:
            logger.info("✓ Database health check passed")
        else:
            logger.error("✗ Database health check failed")
        
        # Get database instance
        db = db_service.get_database()
        logger.info(f"✓ Database instance obtained: {db.name}")
        
        # List collections
        collections = await db.list_collection_names()
        logger.info(f"Existing collections: {collections}")
        
        # Test insert and query
        logger.info("Testing insert operation...")
        test_doc = {
            "username": "test_user",
            "email": "test@example.com",
            "test": True
        }
        
        result = await db.candidates.update_one(
            {"username": "test_user"},
            {"$set": test_doc},
            upsert=True
        )
        logger.info(f"✓ Insert/update successful: matched={result.matched_count}, modified={result.modified_count}")
        
        # Query the document
        found_doc = await db.candidates.find_one({"username": "test_user"})
        if found_doc:
            logger.info(f"✓ Query successful: found document with username={found_doc['username']}")
        
        # Clean up test document
        await db.candidates.delete_one({"username": "test_user"})
        logger.info("✓ Test document cleaned up")
        
        logger.info("=" * 60)
        logger.info("✓ All database tests passed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Database test failed: {str(e)}", exc_info=True)
        raise
    finally:
        # Disconnect
        await db_service.disconnect()


if __name__ == "__main__":
    asyncio.run(test_database_connection())
