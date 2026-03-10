"""Test script for candidate matching endpoint"""
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


async def test_candidate_matching():
    """Test candidate matching endpoint"""
    async with httpx.AsyncClient() as client:
        logger.info("=" * 60)
        logger.info("Testing Candidate Matching Endpoint")
        logger.info("=" * 60)
        
        # Step 1: Create test candidates
        logger.info("\n1. Creating test candidates...")
        
        candidates = [
            {
                "username": "alice_python",
                "email": "alice@example.com",
                "phone": "+1234567890",
                "resume_data": {
                    "extractedText": "Senior Python Developer with 5 years experience in FastAPI, Django, MongoDB, Docker, and AWS. Expert in building scalable microservices.",
                    "skills": ["Python", "FastAPI", "MongoDB", "Docker", "AWS", "Microservices"],
                    "education": ["BS Computer Science - MIT"],
                    "experience": ["Senior Developer at TechCorp - 5 years"]
                },
                "linkedinUrl": "https://linkedin.com/in/alice",
                "githubUrl": "https://github.com/alice"
            },
            {
                "username": "bob_frontend",
                "email": "bob@example.com",
                "phone": "+1234567891",
                "resume_data": {
                    "extractedText": "Frontend Developer specializing in React, TypeScript, CSS, and modern web technologies. 3 years of experience building responsive UIs.",
                    "skills": ["React", "TypeScript", "CSS", "JavaScript", "HTML"],
                    "education": ["BS Software Engineering - Stanford"],
                    "experience": ["Frontend Developer at WebStudio - 3 years"]
                },
                "linkedinUrl": "https://linkedin.com/in/bob",
                "githubUrl": "https://github.com/bob"
            },
            {
                "username": "charlie_fullstack",
                "email": "charlie@example.com",
                "phone": "+1234567892",
                "resume_data": {
                    "extractedText": "Full-stack developer with experience in Python, JavaScript, React, Node.js, and PostgreSQL. Built multiple production applications.",
                    "skills": ["Python", "JavaScript", "React", "Node.js", "PostgreSQL"],
                    "education": ["BS Computer Science - Berkeley"],
                    "experience": ["Full-stack Developer at StartupCo - 4 years"]
                },
                "linkedinUrl": "https://linkedin.com/in/charlie",
                "githubUrl": "https://github.com/charlie"
            }
        ]
        
        for candidate in candidates:
            response = await client.post(f"{BASE_URL}/api/candidates", json=candidate)
            if response.status_code == 200:
                logger.info(f"  ✓ Created candidate: {candidate['username']}")
            else:
                logger.error(f"  ✗ Failed to create candidate: {candidate['username']}")
        
        # Step 2: Get existing jobs
        logger.info("\n2. Fetching existing jobs...")
        response = await client.get(f"{BASE_URL}/api/jobs")
        
        if response.status_code == 200:
            jobs = response.json()
            if jobs:
                job = jobs[0]  # Use the first job
                job_id = job['job_id']
                logger.info(f"  ✓ Using job: {job['title']} at {job['company']}")
                logger.info(f"  - Job ID: {job_id}")
            else:
                logger.error("  ✗ No jobs found. Please create a job first.")
                return
        else:
            logger.error("  ✗ Failed to fetch jobs")
            return
        
        # Step 3: Test candidate matching with default top_k
        logger.info("\n3. Testing candidate matching (default top_k=10)...")
        match_request = {
            "job_id": job_id
        }
        
        response = await client.post(f"{BASE_URL}/api/match-candidates", json=match_request)
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✓ Matching successful")
            logger.info(f"  - Job: {result['job_title']} at {result['company']}")
            logger.info(f"  - Total candidates: {result['total_candidates']}")
            logger.info(f"  - Matches returned: {len(result['matches'])}")
            
            logger.info("\n  Top matches:")
            for i, match in enumerate(result['matches'][:5], 1):
                logger.info(f"    {i}. {match['username']} - Score: {match['similarity_score']}")
                logger.info(f"       Skills: {', '.join(match['skills'][:5])}")
        else:
            logger.error(f"✗ Matching failed: {response.json()}")
            return
        
        # Step 4: Test with custom top_k
        logger.info("\n4. Testing candidate matching (top_k=2)...")
        match_request = {
            "job_id": job_id,
            "top_k": 2
        }
        
        response = await client.post(f"{BASE_URL}/api/match-candidates", json=match_request)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✓ Returned {len(result['matches'])} matches (requested top_k=2)")
        else:
            logger.error("✗ Failed with custom top_k")
        
        # Step 5: Test with non-existent job_id
        logger.info("\n5. Testing with non-existent job_id...")
        match_request = {
            "job_id": "non-existent-job-id"
        }
        
        response = await client.post(f"{BASE_URL}/api/match-candidates", json=match_request)
        
        if response.status_code == 404:
            logger.info("✓ Correctly returned 404 for non-existent job")
        else:
            logger.error(f"✗ Expected 404, got {response.status_code}")
        
        # Step 6: Test without job_id
        logger.info("\n6. Testing without job_id...")
        match_request = {}
        
        response = await client.post(f"{BASE_URL}/api/match-candidates", json=match_request)
        
        if response.status_code == 400:
            logger.info("✓ Correctly returned 400 for missing job_id")
        else:
            logger.error(f"✗ Expected 400, got {response.status_code}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ All candidate matching tests passed!")
        logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_candidate_matching())
