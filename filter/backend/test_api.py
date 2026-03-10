"""Test script for FastAPI endpoints"""
import asyncio
import httpx
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"


async def test_api():
    """Test API endpoints"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            logger.info("=" * 60)
            logger.info("Testing FastAPI Endpoints")
            logger.info("=" * 60)
            
            # Test 1: Root endpoint
            logger.info("\n1. Testing root endpoint...")
            response = await client.get(f"{BASE_URL}/")
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Response: {response.json()}")
            assert response.status_code == 200
            logger.info("✓ Root endpoint works")
            
            # Test 2: Health check
            logger.info("\n2. Testing health check...")
            response = await client.get(f"{BASE_URL}/health")
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Response: {response.json()}")
            assert response.status_code == 200
            assert response.json()["status"] == "ok"
            logger.info("✓ Health check passed")
            
            # Test 3: Create candidate
            logger.info("\n3. Testing candidate creation...")
            candidate_data = {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "resume_data": {
                    "extractedText": "Experienced Python developer with 5 years in web development and machine learning",
                    "skills": ["Python", "FastAPI", "MongoDB", "Machine Learning", "Docker"],
                    "education": ["BS Computer Science - MIT"],
                    "experience": ["Senior Developer at Tech Corp", "ML Engineer at AI Startup"]
                },
                "githubUrl": "https://github.com/johndoe",
                "linkedinUrl": "https://linkedin.com/in/johndoe"
            }
            
            response = await client.post(f"{BASE_URL}/api/candidates", json=candidate_data)
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Response: {json.dumps(response.json(), indent=2)}")
            assert response.status_code == 200
            assert response.json()["success"] == True
            assert response.json()["embedding_dimension"] == 384
            logger.info("✓ Candidate created successfully")
            
            # Test 4: Validation error (missing required field)
            logger.info("\n4. Testing validation error handling...")
            invalid_data = {
                "username": "jane_doe",
                # Missing email (required field)
                "resume_data": {
                    "extractedText": "Test resume",
                    "skills": [],
                    "education": [],
                    "experience": []
                }
            }
            
            response = await client.post(f"{BASE_URL}/api/candidates", json=invalid_data)
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Response: {json.dumps(response.json(), indent=2)}")
            assert response.status_code == 400
            logger.info("✓ Validation error handled correctly")
            
            # Test 5: Update existing candidate
            logger.info("\n5. Testing candidate update...")
            updated_data = candidate_data.copy()
            updated_data["resume_data"]["skills"].append("Kubernetes")
            
            response = await client.post(f"{BASE_URL}/api/candidates", json=updated_data)
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Response: {json.dumps(response.json(), indent=2)}")
            assert response.status_code == 200
            assert response.json()["action"] == "updated"
            logger.info("✓ Candidate updated successfully")
            
            logger.info("\n" + "=" * 60)
            logger.info("✓ All API tests passed!")
            logger.info("=" * 60)
            
        except httpx.ConnectError:
            logger.error("Could not connect to API server. Make sure it's running:")
            logger.error("  uvicorn api.main:app --reload --port 8000")
        except Exception as e:
            logger.error(f"Test failed: {str(e)}", exc_info=True)
            raise


if __name__ == "__main__":
    asyncio.run(test_api())
