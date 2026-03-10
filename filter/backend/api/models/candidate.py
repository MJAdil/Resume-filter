"""Pydantic models for candidate-related requests and responses"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


class ResumeData(BaseModel):
    """Resume data structure"""
    extractedText: str
    skills: List[str] = []
    education: List[str] = []
    experience: List[str] = []


class CandidateCreate(BaseModel):
    """Request model for creating a candidate profile"""
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: Optional[str] = None
    resume_data: ResumeData
    linkedinUrl: Optional[str] = None
    githubUrl: Optional[str] = None
    leetcodeUrl: Optional[str] = None
    codeforcesUrl: Optional[str] = None
