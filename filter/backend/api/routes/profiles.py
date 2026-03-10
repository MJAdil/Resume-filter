"""Profile data fetching API endpoints"""
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import logging
from typing import Dict, Any

from api.models import ProfileFetchRequest
from services.database import db_service
from services.scraper_async import SocialProfileScraper
from config import get_settings

router = APIRouter(prefix="/api", tags=["profiles"])
logger = logging.getLogger(__name__)


@router.post("/fetch-profile-data", status_code=status.HTTP_200_OK)
async def fetch_profile_data(request: ProfileFetchRequest) -> Dict[str, Any]:
    """
    Fetch profile data from external platforms (GitHub, LeetCode, Codeforces, LinkedIn)
    
    - Scrapes data from provided URLs
    - Stores fetched data in candidate's profile_data field
    - Returns success even if some/all fetches fail
    - Includes timestamp and list of successfully fetched platforms
    """
    try:
        logger.info(f"Fetching profile data for: {request.username}")
        logger.info(f"  - URLs provided: {list(request.urls.keys())}")
        
        db = db_service.get_database()
        
        # Verify candidate exists
        candidate = await db.candidates.find_one({"username": request.username})
        
        if not candidate:
            logger.warning(f"  ✗ Candidate not found: {request.username}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate not found: {request.username}"
            )
        
        logger.info(f"  ✓ Candidate found: {request.username}")
        
        # Initialize scraper
        settings = get_settings()
        scraper = SocialProfileScraper(
            linkedin_api_key=settings.linkedin_api_key,
            linkedin_provider=settings.linkedin_provider,
            github_token=settings.github_token
        )
        
        # Scrape all provided URLs
        profile_data = {}
        platforms_fetched = []
        platforms_failed = []
        
        for platform, url in request.urls.items():
            if not url:
                continue
            
            logger.info(f"  - Scraping {platform}: {url}")
            
            try:
                if platform == "github":
                    data = await scraper.scrape_github(url)
                elif platform == "leetcode":
                    data = await scraper.scrape_leetcode(url)
                elif platform == "codeforces":
                    data = await scraper.scrape_codeforces(url)
                elif platform == "linkedin":
                    data = await scraper.scrape_linkedin(url)
                else:
                    logger.warning(f"    ✗ Unknown platform: {platform}")
                    continue
                
                # Check if scraping was successful
                if "error" in data:
                    logger.warning(f"    ✗ Failed: {data['error']}")
                    platforms_failed.append(platform)
                    profile_data[platform] = data  # Store error data
                else:
                    logger.info(f"    ✓ Success")
                    platforms_fetched.append(platform)
                    profile_data[platform] = data
            
            except Exception as e:
                logger.error(f"    ✗ Exception: {str(e)}")
                platforms_failed.append(platform)
                profile_data[platform] = {
                    "error": str(e),
                    "platform": platform
                }
        
        # Update candidate's profile_data in MongoDB
        fetch_timestamp = datetime.utcnow().isoformat()
        
        await db.candidates.update_one(
            {"username": request.username},
            {
                "$set": {
                    "profile_data": profile_data,
                    "profile_data_fetched_at": fetch_timestamp,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"  ✓ Profile data stored for {request.username}")
        logger.info(f"  - Platforms fetched: {platforms_fetched}")
        logger.info(f"  - Platforms failed: {platforms_failed}")
        
        return {
            "success": True,
            "username": request.username,
            "platforms_fetched": platforms_fetched,
            "platforms_failed": platforms_failed,
            "total_platforms_attempted": len(request.urls),
            "fetched_at": fetch_timestamp,
            "message": f"Successfully fetched {len(platforms_fetched)} out of {len(request.urls)} platforms"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching profile data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch profile data: {str(e)}"
        )
