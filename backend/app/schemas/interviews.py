from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class InterviewSessionCreate(BaseModel):
    application_id: UUID


class InterviewFeedback(BaseModel):
    summary: str
    strengths: list[str] = []
    improvements: list[str] = []


class CandidateAnswerCreate(BaseModel):
    answer_text: str = Field(min_length=1)


class CandidateAnswerRead(BaseModel):
    id: UUID
    question_id: UUID
    answer_text: str
    score: float | None
    feedback_json: dict | None
    answered_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InterviewQuestionRead(BaseModel):
    id: UUID
    session_id: UUID
    question_text: str
    question_type: str
    skill_tag: str | None
    expected_signals_json: dict | None
    order_index: int
    created_at: datetime
    answer: CandidateAnswerRead | None = None

    model_config = {"from_attributes": True}


class InterviewSessionRead(BaseModel):
    id: UUID
    application_id: UUID
    candidate_id: UUID
    job_id: UUID
    status: str
    overall_score: float | None
    feedback_json: dict | None
    started_at: datetime
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    questions: list[InterviewQuestionRead] = []

    model_config = {"from_attributes": True}


class InterviewSessionSummary(BaseModel):
    id: UUID
    application_id: UUID
    candidate_id: UUID
    job_id: UUID
    status: str
    overall_score: float | None
    started_at: datetime
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
