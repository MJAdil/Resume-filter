"""Candidate and job matching API endpoints"""
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import logging
from typing import Dict, Any, List
import numpy as np

from api.models import MatchRequest
from services.database import db_service

router = APIRouter(prefix="/api", tags=["matching"])
logger = logging.getLogger(__name__)


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors using dot product
    (assumes vectors are already normalized)
    
    Args:
        vec1: First normalized vector
        vec2: Second normalized vector
    
    Returns:
        Cosine similarity score (0 to 1)
    """
    return float(np.dot(vec1, vec2))


@router.post("/match-candidates", status_code=status.HTTP_200_OK)
async def match_candidates(request: MatchRequest) -> Dict[str, Any]:
    """
    Match candidates to a job based on embedding similarity
    
    - Fetches job embedding from MongoDB
    - Fetches all candidate embeddings
    - Computes cosine similarity scores
    - Returns top_k matches sorted by similarity
    """
    try:
        if not request.job_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="job_id is required for candidate matching"
            )
        
        logger.info(f"Matching candidates for job: {request.job_id}")
        logger.info(f"  - Requested top_k: {request.top_k}")
        
        db = db_service.get_database()
        
        # Fetch job embedding
        job = await db.jobs.find_one({"job_id": request.job_id})
        
        if not job:
            logger.warning(f"  ✗ Job not found: {request.job_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job not found: {request.job_id}"
            )
        
        job_embedding = job.get("embedding")
        if not job_embedding:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Job embedding not found"
            )
        
        logger.info(f"  ✓ Job found: {job.get('title')} at {job.get('company')}")
        
        # Fetch all candidates with embeddings
        cursor = db.candidates.find(
            {"embedding": {"$exists": True}},
            {
                "username": 1,
                "email": 1,
                "phone": 1,
                "resume_data.skills": 1,
                "profile_urls.linkedin": 1,
                "profile_urls.github": 1,
                "embedding": 1
            }
        )
        
        candidates = await cursor.to_list(length=None)
        
        if not candidates:
            logger.info("  ✓ No candidates found in database")
            return {
                "job_id": request.job_id,
                "job_title": job.get("title"),
                "company": job.get("company"),
                "matches": [],
                "total_candidates": 0,
                "top_k": request.top_k
            }
        
        logger.info(f"  - Found {len(candidates)} candidates")
        
        # Calculate similarity scores
        matches = []
        for candidate in candidates:
            candidate_embedding = candidate.get("embedding")
            if not candidate_embedding:
                continue
            
            similarity = cosine_similarity(job_embedding, candidate_embedding)
            
            matches.append({
                "username": candidate.get("username"),
                "email": candidate.get("email"),
                "phone": candidate.get("phone"),
                "skills": candidate.get("resume_data", {}).get("skills", []),
                "linkedin": candidate.get("profile_urls", {}).get("linkedin"),
                "github": candidate.get("profile_urls", {}).get("github"),
                "similarity_score": round(similarity, 4)
            })
        
        # Sort by similarity score (descending) and take top_k
        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        top_matches = matches[:request.top_k]
        
        logger.info(f"  ✓ Computed {len(matches)} similarity scores")
        logger.info(f"  ✓ Returning top {len(top_matches)} matches")
        
        if top_matches:
            logger.info(f"  - Best match: {top_matches[0]['username']} (score: {top_matches[0]['similarity_score']})")
        
        return {
            "job_id": request.job_id,
            "job_title": job.get("title"),
            "company": job.get("company"),
            "matches": top_matches,
            "total_candidates": len(matches),
            "top_k": request.top_k
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error matching candidates: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to match candidates: {str(e)}"
        )



@router.post("/match-jobs", status_code=status.HTTP_200_OK)
async def match_jobs(request: MatchRequest) -> Dict[str, Any]:
    """
    Match jobs to a candidate based on embedding similarity
    
    - Fetches candidate embedding from MongoDB
    - Fetches all job embeddings
    - Computes cosine similarity scores
    - Returns top_k matches sorted by similarity
    """
    try:
        if not request.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="username is required for job matching"
            )
        
        logger.info(f"Matching jobs for candidate: {request.username}")
        logger.info(f"  - Requested top_k: {request.top_k}")
        
        db = db_service.get_database()
        
        # Fetch candidate embedding
        candidate = await db.candidates.find_one({"username": request.username})
        
        if not candidate:
            logger.warning(f"  ✗ Candidate not found: {request.username}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate not found: {request.username}"
            )
        
        candidate_embedding = candidate.get("embedding")
        if not candidate_embedding:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Candidate embedding not found"
            )
        
        logger.info(f"  ✓ Candidate found: {request.username}")
        
        # Fetch all jobs with embeddings
        cursor = db.jobs.find(
            {"embedding": {"$exists": True}},
            {
                "job_id": 1,
                "title": 1,
                "company": 1,
                "location": 1,
                "jobType": 1,
                "salary": 1,
                "embedding": 1
            }
        )
        
        jobs = await cursor.to_list(length=None)
        
        if not jobs:
            logger.info("  ✓ No jobs found in database")
            return {
                "username": request.username,
                "matches": [],
                "total_jobs": 0,
                "top_k": request.top_k
            }
        
        logger.info(f"  - Found {len(jobs)} jobs")
        
        # Calculate similarity scores
        matches = []
        for job in jobs:
            job_embedding = job.get("embedding")
            if not job_embedding:
                continue
            
            similarity = cosine_similarity(candidate_embedding, job_embedding)
            
            matches.append({
                "job_id": job.get("job_id"),
                "job_title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location"),
                "job_type": job.get("jobType"),
                "salary": job.get("salary"),
                "similarity_score": round(similarity, 4)
            })
        
        # Sort by similarity score (descending) and take top_k
        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        top_matches = matches[:request.top_k]
        
        logger.info(f"  ✓ Computed {len(matches)} similarity scores")
        logger.info(f"  ✓ Returning top {len(top_matches)} matches")
        
        if top_matches:
            logger.info(f"  - Best match: {top_matches[0]['job_title']} at {top_matches[0]['company']} (score: {top_matches[0]['similarity_score']})")
        
        return {
            "username": request.username,
            "matches": top_matches,
            "total_jobs": len(matches),
            "top_k": request.top_k
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error matching jobs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to match jobs: {str(e)}"
        )



@router.post("/rank-candidates", status_code=status.HTTP_200_OK)
async def rank_candidates(request: MatchRequest) -> Dict[str, Any]:
    """
    Rank candidates using multi-criteria evaluation with adaptive weights
    
    - Fetches all candidates with profile_data
    - Computes platform scores (GitHub, LeetCode, Codeforces, LinkedIn, Resume)
    - Applies adaptive weight redistribution for missing platforms
    - Returns ranked candidates with scores, weights, and confidence
    """
    try:
        from services.ranking import ranking_service
        
        if not request.job_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="job_id is required for candidate ranking"
            )
        
        logger.info(f"Ranking candidates for job: {request.job_id}")
        logger.info(f"  - Requested top_k: {request.top_k}")
        
        db = db_service.get_database()
        
        # Verify job exists
        job = await db.jobs.find_one({"job_id": request.job_id})
        
        if not job:
            logger.warning(f"  ✗ Job not found: {request.job_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job not found: {request.job_id}"
            )
        
        logger.info(f"  ✓ Job found: {job.get('title')} at {job.get('company')}")
        
        # Fetch all candidates with profile_data
        cursor = db.candidates.find(
            {},
            {
                "username": 1,
                "email": 1,
                "phone": 1,
                "resume_data": 1,
                "profile_data": 1,
                "profile_urls": 1
            }
        )
        
        candidates = await cursor.to_list(length=None)
        
        if not candidates:
            logger.info("  ✓ No candidates found in database")
            return {
                "job_id": request.job_id,
                "job_title": job.get("title"),
                "company": job.get("company"),
                "rankings": [],
                "total_candidates": 0,
                "top_k": request.top_k
            }
        
        logger.info(f"  - Found {len(candidates)} candidates")
        
        # Compute rankings for each candidate
        rankings = []
        for candidate in candidates:
            username = candidate.get("username")
            profile_data = candidate.get("profile_data", {})
            resume_data = candidate.get("resume_data", {})
            
            # Calculate platform scores
            github_score = ranking_service.calculate_github_score(
                profile_data.get("github", {})
            )
            leetcode_score = ranking_service.calculate_leetcode_score(
                profile_data.get("leetcode", {})
            )
            codeforces_score = ranking_service.calculate_codeforces_score(
                profile_data.get("codeforces", {})
            )
            linkedin_score = ranking_service.calculate_linkedin_score(
                profile_data.get("linkedin", {})
            )
            resume_score = ranking_service.calculate_resume_score(resume_data)
            
            platform_scores = {
                "github": github_score,
                "leetcode": leetcode_score,
                "codeforces": codeforces_score,
                "linkedin": linkedin_score,
                "resume": resume_score
            }
            
            # Compute final score with adaptive weights
            final_score, adjusted_weights, confidence = ranking_service.compute_final_score(
                platform_scores
            )
            
            # Calculate completeness
            available_platforms = [p for p, score in platform_scores.items() if score > 0]
            completeness = len(available_platforms) / 5.0
            
            rankings.append({
                "username": username,
                "email": candidate.get("email"),
                "phone": candidate.get("phone"),
                "final_score": round(final_score, 2),
                "platform_scores": {k: round(v, 2) for k, v in platform_scores.items()},
                "adjusted_weights": {k: round(v, 4) for k, v in adjusted_weights.items()},
                "confidence": round(confidence, 2),
                "completeness": round(completeness, 2),
                "available_platforms": available_platforms,
                "linkedin": candidate.get("profile_urls", {}).get("linkedin"),
                "github": candidate.get("profile_urls", {}).get("github")
            })
        
        # Sort by final_score (descending) and take top_k
        rankings.sort(key=lambda x: x["final_score"], reverse=True)
        top_rankings = rankings[:request.top_k]
        
        logger.info(f"  ✓ Computed rankings for {len(rankings)} candidates")
        logger.info(f"  ✓ Returning top {len(top_rankings)} rankings")
        
        if top_rankings:
            logger.info(f"  - Best candidate: {top_rankings[0]['username']} (score: {top_rankings[0]['final_score']}, confidence: {top_rankings[0]['confidence']})")
        
        return {
            "job_id": request.job_id,
            "job_title": job.get("title"),
            "company": job.get("company"),
            "rankings": top_rankings,
            "total_candidates": len(rankings),
            "top_k": request.top_k
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ranking candidates: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rank candidates: {str(e)}"
        )
