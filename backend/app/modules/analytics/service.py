from collections import Counter

from app.core.exceptions import ResourceNotFoundError
from app.models.application import Application
from app.models.interview import InterviewSession
from app.models.job import Job
from app.models.scoring import MatchScore
from app.models.user import User
from app.modules.analytics.repository import AnalyticsRepository
from app.modules.candidates.repository import CandidateRepository
from app.modules.recruiters.repository import RecruiterRepository
from app.schemas.analytics import (
    ApplicationPerJobItem,
    CandidateDashboardResponse,
    DashboardMetricCard,
    PlatformAnalyticsResponse,
    RecentActivityItem,
    RecruiterDashboardResponse,
    SkillCountItem,
    StatusBreakdownItem,
)
from app.services.base import BaseService


class AnalyticsService(BaseService):
    """Dashboard and aggregate metrics service."""

    def __init__(
        self,
        repository: AnalyticsRepository,
        candidate_repository: CandidateRepository,
        recruiter_repository: RecruiterRepository,
    ) -> None:
        self.repository = repository
        self.candidate_repository = candidate_repository
        self.recruiter_repository = recruiter_repository

    def recruiter_dashboard(self, current_user: User) -> RecruiterDashboardResponse:
        recruiter = self.recruiter_repository.get_by_user_id(current_user.id)
        if not recruiter:
            raise ResourceNotFoundError("Recruiter profile not found")

        jobs = self.repository.list_jobs_by_recruiter(recruiter.id)
        applications = self.repository.list_applications_for_recruiter(recruiter.id)
        interviews = self.repository.list_interviews_for_recruiter(recruiter.id)
        scores = [application.match_score for application in applications if application.match_score]

        total_jobs = len(jobs)
        open_jobs = len([job for job in jobs if job.status == "open"])
        closed_jobs = len([job for job in jobs if job.status == "closed"])
        total_applications = len(applications)
        shortlisted = len([application for application in applications if application.status == "shortlisted"])
        accepted = len([application for application in applications if application.status == "accepted"])
        average_match_score = self._average_score(scores)
        average_interview_score = self._average_interview_score(interviews)

        return RecruiterDashboardResponse(
            metric_cards=[
                DashboardMetricCard(label="Total jobs", value=total_jobs),
                DashboardMetricCard(label="Open jobs", value=open_jobs),
                DashboardMetricCard(label="Applications", value=total_applications),
                DashboardMetricCard(label="Avg match score", value=self._display_metric(average_match_score)),
            ],
            total_jobs=total_jobs,
            open_jobs=open_jobs,
            closed_jobs=closed_jobs,
            total_applications=total_applications,
            applications_per_job=[
                ApplicationPerJobItem(job_id=job.id, title=job.title, application_count=len(job.applications))
                for job in jobs
            ],
            shortlisted_candidates=shortlisted,
            accepted_candidates=accepted,
            average_match_score=average_match_score,
            average_interview_score=average_interview_score,
            top_skills_requested=self._top_skills_from_jobs(jobs),
            recent_applications=self._recent_application_items(applications),
            activity_timeline=self._build_timeline(applications, interviews, scores),
        )

    def candidate_dashboard(self, current_user: User) -> CandidateDashboardResponse:
        candidate = self.candidate_repository.get_by_user_id(current_user.id)
        if not candidate:
            raise ResourceNotFoundError("Candidate profile not found")

        applications = self.repository.list_applications_for_candidate(candidate.id)
        interviews = self.repository.list_interviews_for_candidate(candidate.id)
        scores = self.repository.list_scores_for_candidate(candidate.id)
        completed_interviews = len([interview for interview in interviews if interview.status == "completed"])
        pending_interviews = len([interview for interview in interviews if interview.status == "in_progress"])
        average_match_score = self._average_score(scores)
        average_interview_score = self._average_interview_score(interviews)

        return CandidateDashboardResponse(
            metric_cards=[
                DashboardMetricCard(label="Applications", value=len(applications)),
                DashboardMetricCard(label="Completed interviews", value=completed_interviews),
                DashboardMetricCard(label="Avg match score", value=self._display_metric(average_match_score)),
                DashboardMetricCard(label="Avg interview score", value=self._display_metric(average_interview_score)),
            ],
            total_applications=len(applications),
            application_status_breakdown=self._status_breakdown(applications),
            average_match_score=average_match_score,
            average_interview_score=average_interview_score,
            completed_interviews=completed_interviews,
            pending_interviews=pending_interviews,
            top_matched_skills=self._top_matched_skills(scores),
            recent_applications=self._recent_application_items(applications),
            activity_timeline=self._build_timeline(applications, interviews, scores),
        )

    def platform_analytics(self) -> PlatformAnalyticsResponse:
        total_users = self.repository.count_users()
        total_candidates = self.repository.count_candidates()
        total_recruiters = self.repository.count_recruiters()
        total_jobs = self.repository.count_jobs()
        total_applications = self.repository.count_applications()
        total_interviews = self.repository.count_interviews()
        average_match_score = self.repository.average_platform_match_score()

        return PlatformAnalyticsResponse(
            metric_cards=[
                DashboardMetricCard(label="Users", value=total_users),
                DashboardMetricCard(label="Candidates", value=total_candidates),
                DashboardMetricCard(label="Recruiters", value=total_recruiters),
                DashboardMetricCard(label="Applications", value=total_applications),
            ],
            total_users=total_users,
            total_candidates=total_candidates,
            total_recruiters=total_recruiters,
            total_jobs=total_jobs,
            total_applications=total_applications,
            total_interviews=total_interviews,
            average_platform_match_score=average_match_score,
        )

    def _average_score(self, scores: list[MatchScore]) -> float | None:
        if not scores:
            return None
        return round(sum(score.overall_score for score in scores) / len(scores), 2)

    def _average_interview_score(self, interviews: list[InterviewSession]) -> float | None:
        scored = [interview.overall_score for interview in interviews if interview.overall_score is not None]
        if not scored:
            return None
        return round(sum(scored) / len(scored), 2)

    def _display_metric(self, value: float | int | None) -> float | int | str:
        return value if value is not None else "N/A"

    def _top_skills_from_jobs(self, jobs: list[Job]) -> list[SkillCountItem]:
        counter: Counter[str] = Counter()
        for job in jobs:
            for skill in self._as_list(job.skills_json):
                counter[str(skill).strip().lower()] += 1
        return [SkillCountItem(skill=skill, count=count) for skill, count in counter.most_common(10)]

    def _top_matched_skills(self, scores: list[MatchScore]) -> list[SkillCountItem]:
        counter: Counter[str] = Counter()
        for score in scores:
            for skill in self._as_list(score.matched_skills_json):
                counter[str(skill).strip().lower()] += 1
        return [SkillCountItem(skill=skill, count=count) for skill, count in counter.most_common(10)]

    def _status_breakdown(self, applications: list[Application]) -> list[StatusBreakdownItem]:
        counter = Counter(application.status for application in applications)
        return [StatusBreakdownItem(status=status, count=count) for status, count in sorted(counter.items())]

    def _recent_application_items(self, applications: list[Application]) -> list[RecentActivityItem]:
        return [
            RecentActivityItem(
                id=application.id,
                type="application",
                title=f"Application {application.status}",
                description=application.job.title if application.job else None,
                occurred_at=application.applied_at,
            )
            for application in applications[:10]
        ]

    def _build_timeline(
        self,
        applications: list[Application],
        interviews: list[InterviewSession],
        scores: list[MatchScore],
    ) -> list[RecentActivityItem]:
        items: list[RecentActivityItem] = []
        items.extend(self._recent_application_items(applications))
        items.extend(
            RecentActivityItem(
                id=interview.id,
                type="interview",
                title=f"Interview {interview.status}",
                description=f"Score {interview.overall_score}" if interview.overall_score is not None else None,
                occurred_at=interview.completed_at or interview.started_at,
            )
            for interview in interviews[:10]
        )
        items.extend(
            RecentActivityItem(
                id=score.id,
                type="score",
                title="Match score generated",
                description=f"Overall score {score.overall_score}",
                occurred_at=score.updated_at,
            )
            for score in scores[:10]
        )
        return sorted(items, key=lambda item: item.occurred_at, reverse=True)[:15]

    def _as_list(self, value) -> list:
        if value is None:
            return []
        if isinstance(value, list):
            return [item for item in value if item]
        if isinstance(value, dict):
            return [item for item in value.values() if item]
        return [value]
