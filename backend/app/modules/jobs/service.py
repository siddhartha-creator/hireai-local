from uuid import UUID

from app.core.exceptions import PermissionDeniedError, ResourceNotFoundError
from app.models.job import Job
from app.models.user import User
from app.modules.jobs.repository import JobRepository
from app.modules.recruiters.repository import RecruiterRepository
from app.schemas.jobs import JobCreate, JobUpdate
from app.services.base import BaseService


class JobService(BaseService):
    """Job posting business workflows."""

    def __init__(self, job_repository: JobRepository, recruiter_repository: RecruiterRepository) -> None:
        self.job_repository = job_repository
        self.recruiter_repository = recruiter_repository

    def create_job(self, current_user: User, payload: JobCreate) -> Job:
        if self._has_role(current_user, "admin"):
            if payload.recruiter_id is None:
                raise PermissionDeniedError(
                    "Admin job creation requires recruiter_id",
                    details=[{"field": "recruiter_id", "code": "recruiter_id_required"}],
                )
            if not self.recruiter_repository.get_by_id(payload.recruiter_id):
                raise ResourceNotFoundError("Recruiter profile not found", details=[{"code": "recruiter_profile_not_found"}])
            recruiter_id = payload.recruiter_id
        else:
            recruiter_profile = self.recruiter_repository.get_by_user_id(current_user.id)
            if not recruiter_profile:
                raise PermissionDeniedError("Recruiter profile is required to create jobs", details=[{"code": "missing_recruiter_profile"}])
            recruiter_id = recruiter_profile.id
        job = self.job_repository.create(recruiter_id=recruiter_id, payload=payload)
        self.job_repository.db.commit()
        self.job_repository.db.refresh(job)
        return job

    def list_jobs(self, current_user: User) -> list[Job]:
        if self._has_role(current_user, "admin"):
            return self.job_repository.list_all()
        if self._has_role(current_user, "recruiter"):
            recruiter_profile = self.recruiter_repository.get_by_user_id(current_user.id)
            return self.job_repository.list_by_recruiter(recruiter_profile.id) if recruiter_profile else []
        return self.job_repository.list_open()

    def get_job(self, current_user: User, job_id: UUID) -> Job:
        job = self._get_existing_job(job_id)
        if self._has_role(current_user, "admin"):
            return job
        if self._has_role(current_user, "recruiter"):
            self._assert_recruiter_owns_job(current_user, job)
            return job
        if self._has_role(current_user, "candidate") and job.status == "open":
            return job
        raise PermissionDeniedError("Insufficient job permissions", details=[{"code": "job_access_denied"}])

    def update_job(self, current_user: User, job_id: UUID, payload: JobUpdate) -> Job:
        job = self._get_existing_job(job_id)
        if not self._has_role(current_user, "admin"):
            self._assert_recruiter_owns_job(current_user, job)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(job, key, value)
        self.job_repository.db.commit()
        self.job_repository.db.refresh(job)
        return job

    def archive_job(self, current_user: User, job_id: UUID) -> Job:
        job = self._get_existing_job(job_id)
        if not self._has_role(current_user, "admin"):
            self._assert_recruiter_owns_job(current_user, job)
        job.status = "archived"
        self.job_repository.db.commit()
        self.job_repository.db.refresh(job)
        return job

    def _get_existing_job(self, job_id: UUID) -> Job:
        job = self.job_repository.get_by_id(job_id)
        if not job:
            raise ResourceNotFoundError("Job not found", details=[{"code": "job_not_found"}])
        return job

    def _assert_recruiter_owns_job(self, current_user: User, job: Job) -> None:
        recruiter_profile = self.recruiter_repository.get_by_user_id(current_user.id)
        if not recruiter_profile or job.recruiter_id != recruiter_profile.id:
            raise PermissionDeniedError("Recruiter does not own this job", details=[{"code": "job_owner_required"}])

    @staticmethod
    def _has_role(user: User, role_name: str) -> bool:
        return any(role.name == role_name for role in user.roles)
