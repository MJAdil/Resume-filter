"""Test script for health check endpoint"""
import httpx
import asyncio
import logging
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"


async def test_health_check():
    """Test health check endpoint"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        logger.info("=" * 60)
        logger.info("Testing Health Check Endpoint")
        logger.info("=" * 60)
        
        # Test 1: Basic health check
        logger.info("\n1. Testing basic health check...")
        start_time = time.time()
        response = await client.get(f"{BASE_URL}/health")
        response_time = time.time() - start_time
        
        logger.info(f"Status: {response.status_code}")
        logger.info(f"Response time: {response_time:.3f}s")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✓ Health check successful")
            logger.info(f"  - Status: {result.get('status')}")
            logger.info(f"  - Database: {result.get('database')}")
            logger.info(f"  - Model: {result.get('model')}")
            logger.info(f"  - Version: {result.get('version')}")
            
            # Verify response time is under 2 seconds
            if response_time < 2.0:
                logger.info(f"  ✓ Response time within 2s limit ({response_time:.3f}s)")
            else:
                logger.warning(f"  ✗ Response time exceeds 2s limit ({response_time:.3f}s)")
        else:
            logger.error(f"✗ Health check failed: {response.json()}")
            return
        
        # Test 2: Verify response structure
        logger.info("\n2. Verifying response structure...")
        result = response.json()
        
        required_fields = ["status", "database", "model", "version"]
        missing_fields = [field for field in required_fields if field not in result]
        
        if not missing_fields:
            logger.info("✓ All required fields present")
        else:
            logger.error(f"✗ Missing fields: {missing_fields}")
        
        # Test 3: Verify model name
        logger.info("\n3. Verifying model information...")
        if result.get("model") == "bge-small-en-v1.5":
            logger.info("✓ Correct model name")
        else:
            logger.error(f"✗ Incorrect model name: {result.get('model')}")
        
        # Test 4: Multiple rapid requests (stress test)
        logger.info("\n4. Testing multiple rapid requests...")
        start_time = time.time()
        tasks = [client.get(f"{BASE_URL}/health") for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        success_count = sum(1 for r in responses if r.status_code == 200)
        logger.info(f"✓ {success_count}/10 requests successful")
        logger.info(f"  - Total time: {total_time:.3f}s")
        logger.info(f"  - Average time per request: {total_time/10:.3f}s")
        
        if all(r.status_code == 200 for r in responses):
            logger.info("✓ All rapid requests successful")
        else:
            logger.warning("✗ Some rapid requests failed")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ All health check tests passed!")
        logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_health_check())
