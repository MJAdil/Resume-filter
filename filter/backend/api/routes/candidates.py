"""Candidate profile API endpoints"""
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import logging
from typing import Dict, Any

from api.models import CandidateCreate
from services.database import db_service
from services.embeddings import embedding_service

router = APIRouter(prefix="/api", tags=["candidates"])
logger = logging.getLogger(__name__)


@router.post("/candidates", status_code=status.HTTP_200_OK)
async def create_candidate(candidate: CandidateCreate) -> Dict[str, Any]:
    """
    Create or update a candidate profile with resume embedding
    
    - Generates 384-dimension embedding from resume text
    - Stores candidate document in MongoDB
    - Supports upsert behavior (updates if username exists)
    """
    try:
        logger.info(f"Creating candidate profile: {candidate.username}")
        
        # Combine resume fields into single text for embedding
        text_parts = [
            candidate.resume_data.extractedText,
            ' '.join(candidate.resume_data.skills),
            ' '.join(candidate.resume_data.education),
            ' '.join(candidate.resume_data.experience)
        ]
        combined_text = ' '.join(filter(None, text_parts))
        
        logger.info(f"  - Combined text length: {len(combined_text)} chars")
        logger.info(f"  - Skills detected: {len(candidate.resume_data.skills)}")
        
        # Generate embedding
        logger.info("  - Generating embedding...")
        start_time = datetime.utcnow()
        embedding = await embedding_service.generate_embedding(combined_text)
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(f"  ✓ Embedding generated (dimension: {len(embedding)}, duration: {duration:.3f}s)")
        
        # Prepare candidate document (without created_at, will be set via $setOnInsert)
        candidate_doc = {
            "username": candidate.username,
            "email": candidate.email,
            "phone": candidate.phone,
            "resume_data": {
                "extractedText": candidate.resume_data.extractedText,
                "skills": candidate.resume_data.skills,
                "education": candidate.resume_data.education,
                "experience": candidate.resume_data.experience,
                "extractedAt": datetime.utcnow().isoformat()
            },
            "embedding": embedding,
            "embedding_metadata": {
                "model": "bge-small-en-v1.5",
                "dimension": len(embedding),
                "generated_at": datetime.utcnow().isoformat()
            },
            "profile_urls": {
                "linkedin": candidate.linkedinUrl,
                "github": candidate.githubUrl,
                "leetcode": candidate.leetcodeUrl,
                "codeforces": candidate.codeforcesUrl
            },
            "profile_data": {},  # Will be populated by fetch-profile-data endpoint
            "updated_at": datetime.utcnow()
        }
        
        # Store in MongoDB (upsert)
        db = db_service.get_database()
        result = await db.candidates.update_one(
            {"username": candidate.username},
            {
                "$set": candidate_doc,
                "$setOnInsert": {"created_at": datetime.utcnow()}
            },
            upsert=True
        )
        
        action = "updated" if result.matched_count > 0 else "created"
        logger.info(f"  ✓ Candidate profile {action}: {candidate.username}")
        
        return {
            "success": True,
            "username": candidate.username,
            "embedding_dimension": len(embedding),
            "created_at": datetime.utcnow().isoformat(),
            "action": action
        }
    
    except Exception as e:
        logger.error(f"Error creating candidate profile: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create candidate profile: {str(e)}"
        )
