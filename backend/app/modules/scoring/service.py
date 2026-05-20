from uuid import UUID

from app.core.exceptions import PermissionDeniedError, ResourceNotFoundError
from app.models.application import Application
from app.models.job import Job
from app.models.scoring import MatchScore
from app.models.user import User
from app.modules.ai_services.matching.interface import MatchingEngineInterface
from app.modules.applications.repository import ApplicationRepository
from app.modules.candidates.repository import CandidateRepository
from app.modules.jobs.repository import JobRepository
from app.modules.recruiters.repository import RecruiterRepository
from app.modules.resumes.repository import ResumeRepository
from app.modules.scoring.repository import ScoringRepository
from app.schemas.scoring import MatchScoreBreakdown, MatchScoreExplanation, ScoreApplicationResponse
from app.services.base import BaseService


class ScoringService(BaseService):
    """Candidate-job matching score orchestration."""

    def __init__(
        self,
        scoring_repository: ScoringRepository,
        application_repository: ApplicationRepository,
        candidate_repository: CandidateRepository,
        job_repository: JobRepository,
        recruiter_repository: RecruiterRepository,
        resume_repository: ResumeRepository,
        matching_engine: MatchingEngineInterface,
    ) -> None:
        self.scoring_repository = scoring_repository
        self.application_repository = application_repository
        self.candidate_repository = candidate_repository
        self.job_repository = job_repository
        self.recruiter_repository = recruiter_repository
        self.resume_repository = resume_repository
        self.matching_engine = matching_engine

    def score_application(self, current_user: User, application_id: UUID) -> ScoreApplicationResponse:
        application = self._get_existing_application(application_id)
        self._assert_can_access_application(current_user, application)
        candidate = self.candidate_repository.get_by_id(application.candidate_id)
        job = self._get_existing_job(application.job_id)
        if not candidate:
            raise ResourceNotFoundError("Candidate profile not found", details=[{"code": "candidate_profile_not_found"}])
        resume = self.resume_repository.get_primary_by_candidate(candidate.id)
        result = self.matching_engine.score_application(candidate, resume, job)
        score = self.scoring_repository.upsert_for_application(application=application, result=result)
        self.scoring_repository.db.commit()
        self.scoring_repository.db.refresh(score)
        return self._response(score)

    def get_score_for_application(self, current_user: User, application_id: UUID) -> MatchScore:
        application = self._get_existing_application(application_id)
        self._assert_can_access_application(current_user, application)
        score = self.scoring_repository.get_by_application_id(application.id)
        if not score:
            raise ResourceNotFoundError("Match score not found", details=[{"code": "match_score_not_found"}])
        return score

    def list_scores_for_job(self, current_user: User, job_id: UUID) -> list[MatchScore]:
        job = self._get_existing_job(job_id)
        if not self._has_role(current_user, "admin"):
            self._assert_recruiter_owns_job(current_user, job)
        return self.scoring_repository.list_by_job(job.id)

    def list_my_scores(self, current_user: User) -> list[MatchScore]:
        candidate = self.candidate_repository.get_by_user_id(current_user.id)
        return self.scoring_repository.list_by_candidate(candidate.id) if candidate else []

    def list_all_scores(self, current_user: User) -> list[MatchScore]:
        if not self._has_role(current_user, "admin"):
            raise PermissionDeniedError("Admin role is required", details=[{"code": "admin_required"}])
        return self.scoring_repository.list_all()

    def _get_existing_application(self, application_id: UUID) -> Application:
        application = self.application_repository.get_by_id(application_id)
        if not application:
            raise ResourceNotFoundError("Application not found", details=[{"code": "application_not_found"}])
        return application

    def _get_existing_job(self, job_id: UUID) -> Job:
        job = self.job_repository.get_by_id(job_id)
        if not job:
            raise ResourceNotFoundError("Job not found", details=[{"code": "job_not_found"}])
        return job

    def _assert_can_access_application(self, current_user: User, application: Application) -> None:
        if self._has_role(current_user, "admin"):
            return
        if self._has_role(current_user, "candidate"):
            candidate = self.candidate_repository.get_by_user_id(current_user.id)
            if candidate and candidate.id == application.candidate_id:
                return
        if self._has_role(current_user, "recruiter"):
            job = self._get_existing_job(application.job_id)
            self._assert_recruiter_owns_job(current_user, job)
            return
        raise PermissionDeniedError("Insufficient scoring permissions", details=[{"code": "score_access_denied"}])

    def _assert_recruiter_owns_job(self, current_user: User, job: Job) -> None:
        recruiter = self.recruiter_repository.get_by_user_id(current_user.id)
        if not recruiter or recruiter.id != job.recruiter_id:
            raise PermissionDeniedError("Recruiter does not own this job", details=[{"code": "job_owner_required"}])

    def _response(self, score: MatchScore) -> ScoreApplicationResponse:
        return ScoreApplicationResponse(
            score=score,
            breakdown=MatchScoreBreakdown(
                overall_score=score.overall_score,
                skill_score=score.skill_score,
                experience_score=score.experience_score,
                education_score=score.education_score,
                location_score=score.location_score,
            ),
            explanation=MatchScoreExplanation(**score.explanation_json),
        )

    @staticmethod
    def _has_role(user: User, role_name: str) -> bool:
        return any(role.name == role_name for role in user.roles)
