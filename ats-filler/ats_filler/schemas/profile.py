"""Normalized data models for ATS applications."""

from typing import Optional, List
from pydantic import BaseModel, Field


class PersonalInfo(BaseModel):
    """Personal information - maps to 'My Information' section."""
    prefix: Optional[str] = None
    given_name: str
    family_name: str
    email: str
    phone: str
    phone_type: Optional[str] = "Mobile"
    address_line_1: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    canton: Optional[str] = None
    linkedin_url: Optional[str] = None
    how_did_you_hear: Optional[str] = None
    worked_at_company_before: bool = False


class WorkExperience(BaseModel):
    """Work experience entry."""
    job_title: str
    company: str
    location: Optional[str] = None
    currently_work_here: bool = False
    from_month: str  # "02" format
    from_year: str  # "2020" format
    to_month: Optional[str] = None
    to_year: Optional[str] = None
    role_description: Optional[str] = None


class Education(BaseModel):
    """Education entry."""
    school_name: str
    degree: str  # "Master's Degree"
    field_of_study: str
    currently_studying_here: bool = False
    from_month: str
    from_year: str
    to_month: Optional[str] = None
    to_year: Optional[str] = None
    gpa: Optional[str] = None


class Language(BaseModel):
    """Language proficiency."""
    language: str  # "English"
    proficiency: str  # "Native"


class ApplicationProfile(BaseModel):
    """Complete application profile."""
    personal: PersonalInfo
    work_history: List[WorkExperience]
    education_history: List[Education]
    languages: List[Language]
