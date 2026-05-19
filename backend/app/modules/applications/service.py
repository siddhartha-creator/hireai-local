from uuid import UUID

from app.core.exceptions import ConflictError, PermissionDeniedError, ResourceNotFoundError
from app.models.application import Application
from app.models.job import Job
from app.models.user import User
from app.modules.applications.repository import ApplicationRepository
from app.modules.candidates.repository import CandidateRepository
from app.modules.jobs.repository import JobRepository
from app.modules.recruiters.repository import RecruiterRepository
from app.schemas.jobs import ApplicationCreate, ApplicationStatusUpdate
from app.services.base import BaseService


class ApplicationService(BaseService):
    """Application tracking workflows."""

    def __init__(
        self,
        application_repository: ApplicationRepository,
        job_repository: JobRepository,
        candidate_repository: CandidateRepository,
        recruiter_repository: RecruiterRepository,
    ) -> None:
        self.application_repository = application_repository
        self.job_repository = job_repository
        self.candidate_repository = candidate_repository
        self.recruiter_repository = recruiter_repository

    def apply_to_job(self, current_user: User, payload: ApplicationCreate) -> Application:
        candidate_profile = self.candidate_repository.get_by_user_id(current_user.id)
        if not candidate_profile:
            raise PermissionDeniedError("Candidate profile is required to apply", details=[{"code": "missing_candidate_profile"}])
        job = self._get_existing_job(payload.job_id)
        if job.status != "open":
            raise ConflictError("Candidates can only apply to open jobs", details=[{"code": "job_not_open"}])
        existing_application = self.application_repository.get_by_job_and_candidate(
            job_id=job.id,
            candidate_id=candidate_profile.id,
        )
        if existing_application:
            raise ConflictError("Candidate already applied to this job", details=[{"code": "duplicate_application"}])
        application = self.application_repository.create(
            job_id=job.id,
            candidate_id=candidate_profile.id,
            cover_letter=payload.cover_letter,
        )
        self.application_repository.db.commit()
        self.application_repository.db.refresh(application)
        return application

    def list_my_applications(self, current_user: User) -> list[Application]:
        candidate_profile = self.candidate_repository.get_by_user_id(current_user.id)
        return self.application_repository.list_by_candidate(candidate_profile.id) if candidate_profile else []

    def list_all_applications(self, current_user: User) -> list[Application]:
        if not self._has_role(current_user, "admin"):
            raise PermissionDeniedError("Admin role is required", details=[{"code": "admin_required"}])
        return self.application_repository.list_all()

    def list_applications_for_job(self, current_user: User, job_id: UUID) -> list[Application]:
        job = self._get_existing_job(job_id)
        if not self._has_role(current_user, "admin"):
            self._assert_recruiter_owns_job(current_user, job)
        return self.application_repository.list_by_job(job.id)

    def get_application(self, current_user: User, application_id: UUID) -> Application:
        application = self._get_existing_application(application_id)
        if self._has_role(current_user, "admin"):
            return application
        if self._has_role(current_user, "candidate"):
            candidate_profile = self.candidate_repository.get_by_user_id(current_user.id)
            if candidate_profile and application.candidate_id == candidate_profile.id:
                return application
        if self._has_role(current_user, "recruiter"):
            job = self._get_existing_job(application.job_id)
            self._assert_recruiter_owns_job(current_user, job)
            return application
        raise PermissionDeniedError("Insufficient application permissions", details=[{"code": "application_access_denied"}])

    def update_application_status(
        self,
        current_user: User,
        application_id: UUID,
        payload: ApplicationStatusUpdate,
    ) -> Application:
        application = self._get_existing_application(application_id)
        if not self._has_role(current_user, "admin"):
            job = self._get_existing_job(application.job_id)
            self._assert_recruiter_owns_job(current_user, job)
        application.status = payload.status
        self.application_repository.db.commit()
        self.application_repository.db.refresh(application)
        return application

    def _get_existing_job(self, job_id: UUID) -> Job:
        job = self.job_repository.get_by_id(job_id)
        if not job:
            raise ResourceNotFoundError("Job not found", details=[{"code": "job_not_found"}])
        return job

    def _get_existing_application(self, application_id: UUID) -> Application:
        application = self.application_repository.get_by_id(application_id)
        if not application:
            raise ResourceNotFoundError("Application not found", details=[{"code": "application_not_found"}])
        return application

    def _assert_recruiter_owns_job(self, current_user: User, job: Job) -> None:
        recruiter_profile = self.recruiter_repository.get_by_user_id(current_user.id)
        if not recruiter_profile or job.recruiter_id != recruiter_profile.id:
            raise PermissionDeniedError("Recruiter does not own this job", details=[{"code": "job_owner_required"}])

    @staticmethod
    def _has_role(user: User, role_name: str) -> bool:
        return any(role.name == role_name for role in user.roles)
