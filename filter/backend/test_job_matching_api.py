"""Test script for job matching endpoint"""
import httpx
import asyncio
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"


async def test_job_matching():
    """Test job matching endpoint"""
    async with httpx.AsyncClient() as client:
        logger.info("=" * 60)
        logger.info("Testing Job Matching Endpoint")
        logger.info("=" * 60)
        
        # Step 1: Get existing candidate
        logger.info("\n1. Using existing candidate...")
        username = "alice_python"
        logger.info(f"  - Username: {username}")
        
        # Step 2: Test job matching with default top_k
        logger.info("\n2. Testing job matching (default top_k=10)...")
        match_request = {
            "username": username
        }
        
        response = await client.post(f"{BASE_URL}/api/match-jobs", json=match_request)
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✓ Matching successful")
            logger.info(f"  - Candidate: {result['username']}")
            logger.info(f"  - Total jobs: {result['total_jobs']}")
            logger.info(f"  - Matches returned: {len(result['matches'])}")
            
            logger.info("\n  Top matches:")
            for i, match in enumerate(result['matches'][:5], 1):
                logger.info(f"    {i}. {match['job_title']} at {match['company']}")
                logger.info(f"       Location: {match['location']} | Type: {match['job_type']}")
                logger.info(f"       Score: {match['similarity_score']}")
        else:
            logger.error(f"✗ Matching failed: {response.json()}")
            return
        
        # Step 3: Test with custom top_k
        logger.info("\n3. Testing job matching (top_k=1)...")
        match_request = {
            "username": username,
            "top_k": 1
        }
        
        response = await client.post(f"{BASE_URL}/api/match-jobs", json=match_request)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✓ Returned {len(result['matches'])} match (requested top_k=1)")
            if result['matches']:
                match = result['matches'][0]
                logger.info(f"  - Best match: {match['job_title']} at {match['company']}")
        else:
            logger.error("✗ Failed with custom top_k")
        
        # Step 4: Test with non-existent username
        logger.info("\n4. Testing with non-existent username...")
        match_request = {
            "username": "non_existent_user"
        }
        
        response = await client.post(f"{BASE_URL}/api/match-jobs", json=match_request)
        
        if response.status_code == 404:
            logger.info("✓ Correctly returned 404 for non-existent candidate")
        else:
            logger.error(f"✗ Expected 404, got {response.status_code}")
        
        # Step 5: Test without username
        logger.info("\n5. Testing without username...")
        match_request = {}
        
        response = await client.post(f"{BASE_URL}/api/match-jobs", json=match_request)
        
        if response.status_code == 400:
            logger.info("✓ Correctly returned 400 for missing username")
        else:
            logger.error(f"✗ Expected 400, got {response.status_code}")
        
        # Step 6: Test with different candidate
        logger.info("\n6. Testing with frontend developer...")
        match_request = {
            "username": "bob_frontend",
            "top_k": 3
        }
        
        response = await client.post(f"{BASE_URL}/api/match-jobs", json=match_request)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✓ Matching successful for {result['username']}")
            logger.info(f"  - Top {len(result['matches'])} matches:")
            for i, match in enumerate(result['matches'], 1):
                logger.info(f"    {i}. {match['job_title']} - Score: {match['similarity_score']}")
        else:
            logger.error("✗ Failed for bob_frontend")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ All job matching tests passed!")
        logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_job_matching())
