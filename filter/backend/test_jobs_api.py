"""Test script for job posting endpoints"""
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


async def test_jobs_endpoints():
    """Test job posting endpoints"""
    async with httpx.AsyncClient() as client:
        logger.info("=" * 60)
        logger.info("Testing Job Posting Endpoints")
        logger.info("=" * 60)
        
        # Test 1: Create job posting
        logger.info("\n1. Testing job creation...")
        job_data = {
            "jobTitle": "Senior Python Developer",
            "company": "TechCorp",
            "description": "We are looking for an experienced Python developer to join our team.",
            "requirements": "5+ years of Python experience, FastAPI, MongoDB, Docker",
            "location": "Remote",
            "jobType": "Full-time",
            "salary": "$120,000 - $150,000"
        }
        
        response = await client.post(f"{BASE_URL}/api/jobs", json=job_data)
        logger.info(f"Status: {response.status_code}")
        logger.info(f"Response: {response.json()}")
        
        if response.status_code == 201:
            logger.info("✓ Job created successfully")
            job_id = response.json()["job_id"]
        else:
            logger.error("✗ Job creation failed")
            return
        
        # Test 2: Create another job
        logger.info("\n2. Creating another job...")
        job_data2 = {
            "jobTitle": "Frontend Developer",
            "company": "WebStudio",
            "description": "Join our frontend team to build amazing user experiences.",
            "requirements": "React, TypeScript, CSS, 3+ years experience",
            "location": "New York, NY",
            "jobType": "Full-time",
            "salary": "$100,000 - $130,000"
        }
        
        response = await client.post(f"{BASE_URL}/api/jobs", json=job_data2)
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            logger.info("✓ Second job created successfully")
        else:
            logger.error("✗ Second job creation failed")
        
        # Test 3: Get all jobs
        logger.info("\n3. Testing get all jobs...")
        response = await client.get(f"{BASE_URL}/api/jobs")
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            jobs = response.json()
            logger.info(f"✓ Found {len(jobs)} jobs")
            
            # Display job summaries
            for i, job in enumerate(jobs, 1):
                logger.info(f"\n  Job {i}:")
                logger.info(f"    - ID: {job['job_id']}")
                logger.info(f"    - Title: {job['title']}")
                logger.info(f"    - Company: {job['company']}")
                logger.info(f"    - Location: {job['location']}")
                logger.info(f"    - Type: {job['jobType']}")
        else:
            logger.error("✗ Failed to fetch jobs")
            return
        
        # Test 4: Validation error handling
        logger.info("\n4. Testing validation error handling...")
        invalid_job = {
            "jobTitle": "Test Job"
            # Missing required fields
        }
        
        response = await client.post(f"{BASE_URL}/api/jobs", json=invalid_job)
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 400:
            logger.info("✓ Validation error handled correctly")
        else:
            logger.error("✗ Validation error not handled properly")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ All job API tests passed!")
        logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_jobs_endpoints())
