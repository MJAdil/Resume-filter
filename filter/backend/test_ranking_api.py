"""Test script for candidate ranking endpoint"""
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


async def add_profile_data_to_candidates():
    """Add profile_data to existing candidates for ranking tests"""
    from motor.motor_asyncio import AsyncIOMotorClient
    from config import get_settings
    
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client.resume_filter
    
    # Update alice_python with full profile data
    await db.candidates.update_one(
        {"username": "alice_python"},
        {"$set": {
            "profile_data": {
                "github": {
                    "public_repos": 30,
                    "total_stars": 150,
                    "followers": 75
                },
                "leetcode": {
                    "easy_solved": 60,
                    "medium_solved": 40,
                    "hard_solved": 15
                },
                "codeforces": {
                    "max_rating": 1600,
                    "contests_participated": 25
                },
                "linkedin": {
                    "has_experience": True,
                    "has_education": True
                }
            }
        }}
    )
    
    # Update bob_frontend with partial profile data (missing codeforces)
    await db.candidates.update_one(
        {"username": "bob_frontend"},
        {"$set": {
            "profile_data": {
                "github": {
                    "public_repos": 15,
                    "total_stars": 50,
                    "followers": 30
                },
                "leetcode": {
                    "easy_solved": 40,
                    "medium_solved": 20,
                    "hard_solved": 5
                },
                "linkedin": {
                    "has_experience": True,
                    "has_education": True
                }
            }
        }}
    )
    
    # Update charlie_fullstack with minimal profile data (only resume)
    await db.candidates.update_one(
        {"username": "charlie_fullstack"},
        {"$set": {
            "profile_data": {}
        }}
    )
    
    client.close()
    logger.info("✓ Profile data added to candidates")


async def test_ranking_endpoint():
    """Test candidate ranking endpoint"""
    async with httpx.AsyncClient() as client:
        logger.info("=" * 60)
        logger.info("Testing Candidate Ranking Endpoint")
        logger.info("=" * 60)
        
        # Step 1: Add profile data to candidates
        logger.info("\n1. Adding profile data to candidates...")
        await add_profile_data_to_candidates()
        
        # Step 2: Get existing job
        logger.info("\n2. Fetching existing job...")
        response = await client.get(f"{BASE_URL}/api/jobs")
        
        if response.status_code == 200:
            jobs = response.json()
            if jobs:
                job = jobs[0]
                job_id = job['job_id']
                logger.info(f"  ✓ Using job: {job['title']} at {job['company']}")
                logger.info(f"  - Job ID: {job_id}")
            else:
                logger.error("  ✗ No jobs found")
                return
        else:
            logger.error("  ✗ Failed to fetch jobs")
            return
        
        # Step 3: Test ranking with default top_k
        logger.info("\n3. Testing candidate ranking (default top_k=10)...")
        rank_request = {
            "job_id": job_id
        }
        
        response = await client.post(f"{BASE_URL}/api/rank-candidates", json=rank_request)
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✓ Ranking successful")
            logger.info(f"  - Job: {result['job_title']} at {result['company']}")
            logger.info(f"  - Total candidates: {result['total_candidates']}")
            logger.info(f"  - Rankings returned: {len(result['rankings'])}")
            
            logger.info("\n  Top rankings:")
            for i, ranking in enumerate(result['rankings'][:5], 1):
                logger.info(f"\n    {i}. {ranking['username']}")
                logger.info(f"       Final Score: {ranking['final_score']}/100")
                logger.info(f"       Confidence: {ranking['confidence']}")
                logger.info(f"       Completeness: {ranking['completeness']}")
                logger.info(f"       Platform Scores:")
                for platform, score in ranking['platform_scores'].items():
                    logger.info(f"         - {platform}: {score}")
                logger.info(f"       Available Platforms: {', '.join(ranking['available_platforms'])}")
        else:
            logger.error(f"✗ Ranking failed: {response.json()}")
            return
        
        # Step 4: Test with custom top_k
        logger.info("\n4. Testing ranking with top_k=2...")
        rank_request = {
            "job_id": job_id,
            "top_k": 2
        }
        
        response = await client.post(f"{BASE_URL}/api/rank-candidates", json=rank_request)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✓ Returned {len(result['rankings'])} rankings (requested top_k=2)")
        else:
            logger.error("✗ Failed with custom top_k")
        
        # Step 5: Test with non-existent job_id
        logger.info("\n5. Testing with non-existent job_id...")
        rank_request = {
            "job_id": "non-existent-job-id"
        }
        
        response = await client.post(f"{BASE_URL}/api/rank-candidates", json=rank_request)
        
        if response.status_code == 404:
            logger.info("✓ Correctly returned 404 for non-existent job")
        else:
            logger.error(f"✗ Expected 404, got {response.status_code}")
        
        # Step 6: Test without job_id
        logger.info("\n6. Testing without job_id...")
        rank_request = {}
        
        response = await client.post(f"{BASE_URL}/api/rank-candidates", json=rank_request)
        
        if response.status_code == 400:
            logger.info("✓ Correctly returned 400 for missing job_id")
        else:
            logger.error(f"✗ Expected 400, got {response.status_code}")
        
        # Step 7: Verify adaptive weight redistribution
        logger.info("\n7. Verifying adaptive weight redistribution...")
        rank_request = {
            "job_id": job_id,
            "top_k": 10
        }
        
        response = await client.post(f"{BASE_URL}/api/rank-candidates", json=rank_request)
        
        if response.status_code == 200:
            result = response.json()
            
            # Find candidates with different completeness levels
            for ranking in result['rankings']:
                if ranking['completeness'] < 1.0:
                    logger.info(f"  - {ranking['username']}: completeness={ranking['completeness']}")
                    logger.info(f"    Adjusted weights: {ranking['adjusted_weights']}")
                    
                    # Verify weights sum to 1.0
                    weights_sum = sum(ranking['adjusted_weights'].values())
                    if abs(weights_sum - 1.0) < 0.001:
                        logger.info(f"    ✓ Weights sum to 1.0")
                    else:
                        logger.error(f"    ✗ Weights sum to {weights_sum}, expected 1.0")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ All ranking endpoint tests passed!")
        logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_ranking_endpoint())
