"""Pydantic models for general API requests"""
from pydantic import BaseModel, Field
from typing import Optional, Dict


class MatchRequest(BaseModel):
    """Request model for matching candidates or jobs"""
    job_id: Optional[str] = None
    username: Optional[str] = None
    top_k: int = Field(default=10, ge=1, le=100)


class ProfileFetchRequest(BaseModel):
    """Request model for fetching profile data from external platforms"""
    username: str
    urls: Dict[str, str] = {}
