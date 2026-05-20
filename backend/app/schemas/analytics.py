from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DashboardMetricCard(BaseModel):
    label: str
    value: int | float | str
    helper_text: str | None = None


class RecentActivityItem(BaseModel):
    id: UUID
    type: str
    title: str
    description: str | None = None
    occurred_at: datetime


class ApplicationPerJobItem(BaseModel):
    job_id: UUID
    title: str
    application_count: int


class StatusBreakdownItem(BaseModel):
    status: str
    count: int


class SkillCountItem(BaseModel):
    skill: str
    count: int


class RecruiterDashboardResponse(BaseModel):
    metric_cards: list[DashboardMetricCard]
    total_jobs: int
    open_jobs: int
    closed_jobs: int
    total_applications: int
    applications_per_job: list[ApplicationPerJobItem]
    shortlisted_candidates: int
    accepted_candidates: int
    average_match_score: float | None
    average_interview_score: float | None
    top_skills_requested: list[SkillCountItem]
    recent_applications: list[RecentActivityItem]
    activity_timeline: list[RecentActivityItem]


class CandidateDashboardResponse(BaseModel):
    metric_cards: list[DashboardMetricCard]
    total_applications: int
    application_status_breakdown: list[StatusBreakdownItem]
    average_match_score: float | None
    average_interview_score: float | None
    completed_interviews: int
    pending_interviews: int
    top_matched_skills: list[SkillCountItem]
    recent_applications: list[RecentActivityItem]
    activity_timeline: list[RecentActivityItem]


class PlatformAnalyticsResponse(BaseModel):
    metric_cards: list[DashboardMetricCard]
    total_users: int
    total_candidates: int
    total_recruiters: int
    total_jobs: int
    total_applications: int
    total_interviews: int
    average_platform_match_score: float | None
