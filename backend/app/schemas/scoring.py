from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MatchScoreBreakdown(BaseModel):
    overall_score: float
    skill_score: float
    experience_score: float
    education_score: float
    location_score: float


class MatchScoreExplanation(BaseModel):
    summary: str
    skill_reason: str
    experience_reason: str
    education_reason: str
    location_reason: str
    recommendation: str


class MatchScoreRead(BaseModel):
    id: UUID
    application_id: UUID
    candidate_id: UUID
    job_id: UUID
    overall_score: float
    skill_score: float
    experience_score: float
    education_score: float
    location_score: float
    explanation_json: dict
    matched_skills_json: list
    missing_skills_json: list
    scoring_version: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MatchScoreListItem(MatchScoreRead):
    pass


class ScoreApplicationResponse(BaseModel):
    score: MatchScoreRead
    breakdown: MatchScoreBreakdown
    explanation: MatchScoreExplanation
