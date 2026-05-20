from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.models.application import Application
from app.models.candidate import CandidateProfile
from app.models.interview import InterviewSession
from app.models.job import Job
from app.models.recruiter import RecruiterProfile
from app.models.scoring import MatchScore
from app.models.user import User
from app.repositories.base import BaseRepository


class AnalyticsRepository(BaseRepository):
    """Read-only dashboard analytics queries."""

    def list_jobs_by_recruiter(self, recruiter_id) -> list[Job]:
        return (
            self.db.query(Job)
            .filter(Job.recruiter_id == recruiter_id)
            .options(joinedload(Job.applications), joinedload(Job.match_scores))
            .order_by(Job.created_at.desc())
            .all()
        )

    def list_applications_for_recruiter(self, recruiter_id) -> list[Application]:
        return (
            self.db.query(Application)
            .join(Job, Application.job_id == Job.id)
            .filter(Job.recruiter_id == recruiter_id)
            .options(joinedload(Application.job), joinedload(Application.match_score))
            .order_by(Application.applied_at.desc())
            .all()
        )

    def list_interviews_for_recruiter(self, recruiter_id) -> list[InterviewSession]:
        return (
            self.db.query(InterviewSession)
            .join(Job, InterviewSession.job_id == Job.id)
            .filter(Job.recruiter_id == recruiter_id)
            .order_by(InterviewSession.created_at.desc())
            .all()
        )

    def list_applications_for_candidate(self, candidate_id) -> list[Application]:
        return (
            self.db.query(Application)
            .filter(Application.candidate_id == candidate_id)
            .options(joinedload(Application.job), joinedload(Application.match_score))
            .order_by(Application.applied_at.desc())
            .all()
        )

    def list_interviews_for_candidate(self, candidate_id) -> list[InterviewSession]:
        return (
            self.db.query(InterviewSession)
            .filter(InterviewSession.candidate_id == candidate_id)
            .order_by(InterviewSession.created_at.desc())
            .all()
        )

    def list_scores_for_candidate(self, candidate_id) -> list[MatchScore]:
        return (
            self.db.query(MatchScore)
            .filter(MatchScore.candidate_id == candidate_id)
            .order_by(MatchScore.created_at.desc())
            .all()
        )

    def count_users(self) -> int:
        return self.db.query(func.count(User.id)).scalar() or 0

    def count_candidates(self) -> int:
        return self.db.query(func.count(CandidateProfile.id)).scalar() or 0

    def count_recruiters(self) -> int:
        return self.db.query(func.count(RecruiterProfile.id)).scalar() or 0

    def count_jobs(self) -> int:
        return self.db.query(func.count(Job.id)).scalar() or 0

    def count_applications(self) -> int:
        return self.db.query(func.count(Application.id)).scalar() or 0

    def count_interviews(self) -> int:
        return self.db.query(func.count(InterviewSession.id)).scalar() or 0

    def average_platform_match_score(self) -> float | None:
        value = self.db.query(func.avg(MatchScore.overall_score)).scalar()
        return round(float(value), 2) if value is not None else None
