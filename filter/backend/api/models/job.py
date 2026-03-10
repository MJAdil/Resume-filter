"""Pydantic models for job-related requests and responses"""
from pydantic import BaseModel, Field
from typing import Optional


class JobCreate(BaseModel):
    """Request model for creating a job posting"""
    jobTitle: str = Field(..., min_length=1)
    company: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    requirements: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    jobType: str = Field(..., min_length=1)
    salary: Optional[str] = None
