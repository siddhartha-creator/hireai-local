from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


JobStatus = Literal["draft", "open", "closed", "archived"]
EmploymentType = Literal["full_time", "part_time", "internship", "contract", "remote"]
ApplicationStatus = Literal["submitted", "under_review", "shortlisted", "rejected", "accepted", "withdrawn"]


class JobCreate(BaseModel):
    recruiter_id: UUID | None = None
    title: str = Field(min_length=2, max_length=255)
    description: str = Field(min_length=10)
    requirements_json: list | dict | None = None
    skills_json: list | dict | None = None
    seniority: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=255)
    employment_type: EmploymentType | None = None
    salary_min: float | None = Field(default=None, ge=0)
    salary_max: float | None = Field(default=None, ge=0)
    status: JobStatus = "draft"

    @model_validator(mode="after")
    def validate_salary_range(self):
        if self.salary_min is not None and self.salary_max is not None and self.salary_min > self.salary_max:
            raise ValueError("salary_min cannot be greater than salary_max")
        return self


class JobUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = Field(default=None, min_length=10)
    requirements_json: list | dict | None = None
    skills_json: list | dict | None = None
    seniority: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=255)
    employment_type: EmploymentType | None = None
    salary_min: float | None = Field(default=None, ge=0)
    salary_max: float | None = Field(default=None, ge=0)
    status: JobStatus | None = None

    @model_validator(mode="after")
    def validate_salary_range(self):
        if self.salary_min is not None and self.salary_max is not None and self.salary_min > self.salary_max:
            raise ValueError("salary_min cannot be greater than salary_max")
        return self


class JobListItem(BaseModel):
    id: UUID
    recruiter_id: UUID
    title: str
    seniority: str | None
    location: str | None
    employment_type: str | None
    salary_min: float | None
    salary_max: float | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class JobRead(JobListItem):
    description: str
    requirements_json: list | dict | None
    skills_json: list | dict | None
    updated_at: datetime


class ApplicationCreate(BaseModel):
    job_id: UUID
    cover_letter: str | None = None


class ApplicationRead(BaseModel):
    id: UUID
    job_id: UUID
    candidate_id: UUID
    status: str
    cover_letter: str | None
    applied_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
