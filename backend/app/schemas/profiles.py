from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class CandidateProfileUpdate(BaseModel):
    headline: str | None = Field(default=None, max_length=255)
    summary: str | None = None
    phone: str | None = Field(default=None, max_length=50)
    location: str | None = Field(default=None, max_length=255)
    skills_json: list | dict | None = None
    education_json: list | dict | None = None
    experience_json: list | dict | None = None
    experience_years: int | None = Field(default=None, ge=0)
    portfolio_url: HttpUrl | None = None
    linkedin_url: HttpUrl | None = None
    github_url: HttpUrl | None = None


class CandidateProfileRead(BaseModel):
    id: UUID
    user_id: UUID
    headline: str | None
    summary: str | None
    phone: str | None
    location: str | None
    skills_json: list | dict | None
    education_json: list | dict | None
    experience_json: list | dict | None
    experience_years: int | None
    portfolio_url: str | None
    linkedin_url: str | None
    github_url: str | None
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecruiterProfileUpdate(BaseModel):
    company_name: str | None = Field(default=None, max_length=255)
    company_website: HttpUrl | None = None
    company_size: str | None = Field(default=None, max_length=100)
    industry: str | None = Field(default=None, max_length=255)
    position: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    location: str | None = Field(default=None, max_length=255)
    company_description: str | None = None


class RecruiterProfileRead(BaseModel):
    id: UUID
    user_id: UUID
    company_name: str | None
    company_website: str | None
    company_size: str | None
    industry: str | None
    position: str | None
    phone: str | None
    location: str | None
    company_description: str | None
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
