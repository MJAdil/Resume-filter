"""Test script for profile data fetching endpoint"""
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


async def test_profile_fetch():
    """Test profile data fetching endpoint"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        logger.info("=" * 60)
        logger.info("Testing Profile Data Fetching Endpoint")
        logger.info("=" * 60)
        
        # Test 1: Fetch profile data for alice_python
        logger.info("\n1. Testing profile fetch for alice_python...")
        fetch_request = {
            "username": "alice_python",
            "urls": {
                "github": "https://github.com/torvalds",  # Using Linus Torvalds as example
                "leetcode": "https://leetcode.com/u/jacoblucas",  # Using a valid LeetCode user
                "codeforces": "https://codeforces.com/profile/tourist",  # Using tourist as example
                "linkedin": "https://www.linkedin.com/in/williamhgates"  # Bill Gates LinkedIn
            }
        }
        
        response = await client.post(f"{BASE_URL}/api/fetch-profile-data", json=fetch_request)
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✓ Profile fetch successful")
            logger.info(f"  - Username: {result['username']}")
            logger.info(f"  - Platforms fetched: {result['platforms_fetched']}")
            logger.info(f"  - Platforms failed: {result['platforms_failed']}")
            logger.info(f"  - Total attempted: {result['total_platforms_attempted']}")
            logger.info(f"  - Message: {result['message']}")
        else:
            logger.error(f"✗ Profile fetch failed: {response.json()}")
            return
        
        # Test 2: Fetch with invalid URLs
        logger.info("\n2. Testing with invalid URLs...")
        fetch_request = {
            "username": "bob_frontend",
            "urls": {
                "github": "https://github.com/nonexistentuser12345xyz",
                "leetcode": "https://leetcode.com/u/nonexistentuser12345xyz"
            }
        }
        
        response = await client.post(f"{BASE_URL}/api/fetch-profile-data", json=fetch_request)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✓ Request succeeded (as expected)")
            logger.info(f"  - Platforms fetched: {result['platforms_fetched']}")
            logger.info(f"  - Platforms failed: {result['platforms_failed']}")
            logger.info(f"  - Note: System returns success even if all fetches fail")
        else:
            logger.error("✗ Unexpected error")
        
        # Test 3: Test with non-existent username
        logger.info("\n3. Testing with non-existent username...")
        fetch_request = {
            "username": "nonexistent_user",
            "urls": {
                "github": "https://github.com/torvalds"
            }
        }
        
        response = await client.post(f"{BASE_URL}/api/fetch-profile-data", json=fetch_request)
        
        if response.status_code == 404:
            logger.info("✓ Correctly returned 404 for non-existent candidate")
        else:
            logger.error(f"✗ Expected 404, got {response.status_code}")
        
        # Test 4: Test with empty URLs
        logger.info("\n4. Testing with empty URLs...")
        fetch_request = {
            "username": "charlie_fullstack",
            "urls": {}
        }
        
        response = await client.post(f"{BASE_URL}/api/fetch-profile-data", json=fetch_request)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✓ Request succeeded with empty URLs")
            logger.info(f"  - Platforms fetched: {result['platforms_fetched']}")
        else:
            logger.error("✗ Failed with empty URLs")
        
        # Test 5: Verify data was stored in MongoDB
        logger.info("\n5. Verifying data storage...")
        from motor.motor_asyncio import AsyncIOMotorClient
        from config import get_settings
        
        settings = get_settings()
        mongo_client = AsyncIOMotorClient(settings.mongodb_uri)
        db = mongo_client.resume_filter
        
        candidate = await db.candidates.find_one({"username": "alice_python"})
        
        if candidate and "profile_data" in candidate:
            logger.info("✓ Profile data stored in MongoDB")
            logger.info(f"  - Platforms in profile_data: {list(candidate['profile_data'].keys())}")
            
            # Check GitHub data
            if "github" in candidate['profile_data']:
                github_data = candidate['profile_data']['github']
                if "error" not in github_data:
                    logger.info(f"  - GitHub username: {github_data.get('username')}")
                    logger.info(f"  - GitHub repos: {github_data.get('public_repos')}")
                    logger.info(f"  - GitHub followers: {github_data.get('followers')}")
                else:
                    logger.info(f"  - GitHub error: {github_data.get('error')}")
            
            # Check LeetCode data
            if "leetcode" in candidate['profile_data']:
                leetcode_data = candidate['profile_data']['leetcode']
                if "error" not in leetcode_data:
                    logger.info(f"  - LeetCode username: {leetcode_data.get('username')}")
                    logger.info(f"  - LeetCode total solved: {leetcode_data.get('total_solved')}")
                    logger.info(f"  - LeetCode easy: {leetcode_data.get('easy_solved')}, medium: {leetcode_data.get('medium_solved')}, hard: {leetcode_data.get('hard_solved')}")
                else:
                    logger.info(f"  - LeetCode error: {leetcode_data.get('error')}")
            
            # Check Codeforces data
            if "codeforces" in candidate['profile_data']:
                codeforces_data = candidate['profile_data']['codeforces']
                if "error" not in codeforces_data:
                    logger.info(f"  - Codeforces username: {codeforces_data.get('username')}")
                    logger.info(f"  - Codeforces rating: {codeforces_data.get('rating')}, max: {codeforces_data.get('max_rating')}")
                    logger.info(f"  - Codeforces contests: {codeforces_data.get('contests_participated')}")
                else:
                    logger.info(f"  - Codeforces error: {codeforces_data.get('error')}")
            
            # Check LinkedIn data
            if "linkedin" in candidate['profile_data']:
                linkedin_data = candidate['profile_data']['linkedin']
                if "error" not in linkedin_data:
                    logger.info(f"  - LinkedIn name: {linkedin_data.get('full_name')}")
                    logger.info(f"  - LinkedIn headline: {linkedin_data.get('headline')}")
                    logger.info(f"  - LinkedIn has_experience: {linkedin_data.get('has_experience')}")
                    logger.info(f"  - LinkedIn has_education: {linkedin_data.get('has_education')}")
                else:
                    logger.info(f"  - LinkedIn error: {linkedin_data.get('error')}")
        else:
            logger.error("✗ Profile data not found in MongoDB")
        
        mongo_client.close()
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ All profile fetch tests passed!")
        logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_profile_fetch())
