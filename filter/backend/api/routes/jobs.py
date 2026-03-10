"""Job posting API endpoints"""
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import logging
from typing import Dict, Any, List
import uuid

from api.models import JobCreate
from services.database import db_service
from services.embeddings import embedding_service

router = APIRouter(prefix="/api", tags=["jobs"])
logger = logging.getLogger(__name__)


@router.post("/jobs", status_code=status.HTTP_201_CREATED)
async def create_job(job: JobCreate) -> Dict[str, Any]:
    """
    Create a job posting with embedding
    
    - Generates unique job_id using UUID
    - Generates 384-dimension embedding from job description and requirements
    - Stores job document in MongoDB
    """
    try:
        # Generate unique job_id
        job_id = str(uuid.uuid4())
        logger.info(f"Creating job posting: {job_id}")
        
        # Combine job fields into single text for embedding
        text_parts = [
            job.jobTitle,
            job.company,
            job.description,
            job.requirements,
            job.location,
            job.jobType
        ]
        combined_text = ' '.join(filter(None, text_parts))
        
        logger.info(f"  - Combined text length: {len(combined_text)} chars")
        
        # Generate embedding
        logger.info("  - Generating embedding...")
        start_time = datetime.utcnow()
        embedding = await embedding_service.generate_embedding(combined_text)
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(f"  ✓ Embedding generated (dimension: {len(embedding)}, duration: {duration:.3f}s)")
        
        # Prepare job document
        job_doc = {
            "job_id": job_id,
            "title": job.jobTitle,
            "company": job.company,
            "description": job.description,
            "requirements": job.requirements,
            "location": job.location,
            "jobType": job.jobType,
            "salary": job.salary,
            "embedding": embedding,
            "embedding_metadata": {
                "model": "bge-small-en-v1.5",
                "dimension": len(embedding),
                "generated_at": datetime.utcnow().isoformat()
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Store in MongoDB
        db = db_service.get_database()
        await db.jobs.insert_one(job_doc)
        
        logger.info(f"  ✓ Job posting created: {job_id}")
        
        return {
            "success": True,
            "job_id": job_id,
            "embedding_dimension": len(embedding),
            "created_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error creating job posting: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job posting: {str(e)}"
        )


@router.get("/jobs", status_code=status.HTTP_200_OK)
async def get_jobs() -> List[Dict[str, Any]]:
    """
    Fetch all job postings
    
    - Returns all jobs sorted by created_at (newest first)
    - Excludes embedding vectors from response for efficiency
    """
    try:
        logger.info("Fetching all job postings")
        
        db = db_service.get_database()
        cursor = db.jobs.find(
            {},
            {"embedding": 0}  # Exclude embedding vector from response
        ).sort("created_at", -1)  # Sort by newest first
        
        jobs = await cursor.to_list(length=None)
        
        # Convert ObjectId to string for JSON serialization
        for job in jobs:
            if "_id" in job:
                job["_id"] = str(job["_id"])
            if "created_at" in job:
                job["created_at"] = job["created_at"].isoformat()
            if "updated_at" in job:
                job["updated_at"] = job["updated_at"].isoformat()
        
        logger.info(f"  ✓ Found {len(jobs)} job postings")
        
        return jobs
    
    except Exception as e:
        logger.error(f"Error fetching job postings: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch job postings: {str(e)}"
        )
