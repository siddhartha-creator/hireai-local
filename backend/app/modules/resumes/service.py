from pathlib import Path
from uuid import UUID

from fastapi import UploadFile

from app.core.exceptions import ConflictError, PermissionDeniedError, ResourceNotFoundError
from app.models.resume import Resume
from app.models.user import User
from app.modules.applications.repository import ApplicationRepository
from app.modules.candidates.repository import CandidateRepository
from app.modules.jobs.repository import JobRepository
from app.modules.recruiters.repository import RecruiterRepository
from app.modules.resumes.parser import ResumeParserService
from app.modules.resumes.repository import ResumeRepository
from app.modules.resumes.skills import SkillExtractionService
from app.modules.resumes.storage import ResumeStorageService
from app.schemas.resumes import ResumeUploadResponse
from app.services.base import BaseService


class ResumeService(BaseService):
    """Resume upload, storage, parsing, and access-control orchestration."""

    ALLOWED_FILE_TYPES = {"pdf", "docx"}
    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

    def __init__(
        self,
        resume_repository: ResumeRepository,
        candidate_repository: CandidateRepository,
        recruiter_repository: RecruiterRepository,
        job_repository: JobRepository,
        application_repository: ApplicationRepository,
        storage_service: ResumeStorageService,
        parser_service: ResumeParserService,
        skill_extraction_service: SkillExtractionService,
    ) -> None:
        self.resume_repository = resume_repository
        self.candidate_repository = candidate_repository
        self.recruiter_repository = recruiter_repository
        self.job_repository = job_repository
        self.application_repository = application_repository
        self.storage_service = storage_service
        self.parser_service = parser_service
        self.skill_extraction_service = skill_extraction_service

    async def upload_resume(self, current_user: User, file: UploadFile) -> ResumeUploadResponse:
        candidate_profile = self.candidate_repository.get_by_user_id(current_user.id)
        if not candidate_profile:
            raise PermissionDeniedError("Candidate profile is required to upload resumes", details=[{"code": "missing_candidate_profile"}])

        original_file_name = Path(file.filename or "resume").name
        file_type = self._extract_file_type(original_file_name)
        if file_type not in self.ALLOWED_FILE_TYPES:
            raise ConflictError("Only PDF and DOCX resumes are allowed", details=[{"code": "invalid_file_type"}])

        content = await file.read()
        file_size = len(content)
        if file_size > self.MAX_FILE_SIZE_BYTES:
            raise ConflictError("Resume file exceeds 5MB limit", details=[{"code": "file_too_large"}])

        extracted_text = self.parser_service.extract_text(content=content, file_type=file_type)
        extracted_skills = self.skill_extraction_service.extract(extracted_text)
        parsed_data = self.parser_service.build_parsed_data(text=extracted_text, skills=extracted_skills)
        file_name, file_path = self.storage_service.save(content=content, file_type=file_type)
        is_primary = not self.resume_repository.has_any_for_candidate(candidate_profile.id)

        resume = self.resume_repository.create(
            candidate_id=candidate_profile.id,
            file_name=file_name,
            original_file_name=original_file_name,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            extracted_text=extracted_text,
            parsed_data_json=parsed_data.model_dump(),
            extracted_skills_json=extracted_skills,
            is_primary=is_primary,
        )
        self.resume_repository.db.commit()
        self.resume_repository.db.refresh(resume)
        return ResumeUploadResponse(resume=resume, parsed_data=parsed_data)

    def list_my_resumes(self, current_user: User) -> list[Resume]:
        candidate_profile = self.candidate_repository.get_by_user_id(current_user.id)
        return self.resume_repository.list_by_candidate(candidate_profile.id) if candidate_profile else []

    def get_resume(self, current_user: User, resume_id: UUID) -> Resume:
        resume = self._get_existing_resume(resume_id)
        self._assert_can_access_resume(current_user, resume)
        return resume

    def get_parsed_resume(self, current_user: User, resume_id: UUID) -> dict:
        resume = self.get_resume(current_user, resume_id)
        return resume.parsed_data_json or {}

    def mark_primary(self, current_user: User, resume_id: UUID) -> Resume:
        resume = self._get_existing_resume(resume_id)
        self._assert_candidate_owns_resume(current_user, resume)
        self.resume_repository.unset_primary_for_candidate(resume.candidate_id)
        resume.is_primary = True
        self.resume_repository.db.commit()
        self.resume_repository.db.refresh(resume)
        return resume

    def delete_resume(self, current_user: User, resume_id: UUID) -> None:
        resume = self._get_existing_resume(resume_id)
        self._assert_candidate_owns_resume(current_user, resume)
        file_path = resume.file_path
        self.resume_repository.delete(resume)
        self.resume_repository.db.commit()
        self.storage_service.delete(file_path)

    def _get_existing_resume(self, resume_id: UUID) -> Resume:
        resume = self.resume_repository.get_by_id(resume_id)
        if not resume:
            raise ResourceNotFoundError("Resume not found", details=[{"code": "resume_not_found"}])
        return resume

    def _assert_candidate_owns_resume(self, current_user: User, resume: Resume) -> None:
        candidate_profile = self.candidate_repository.get_by_user_id(current_user.id)
        if not candidate_profile or resume.candidate_id != candidate_profile.id:
            raise PermissionDeniedError("Candidate does not own this resume", details=[{"code": "resume_owner_required"}])

    def _assert_can_access_resume(self, current_user: User, resume: Resume) -> None:
        if self._has_role(current_user, "admin"):
            return
        if self._has_role(current_user, "candidate"):
            self._assert_candidate_owns_resume(current_user, resume)
            return
        if self._has_role(current_user, "recruiter") and self._recruiter_has_candidate_application(current_user, resume):
            return
        raise PermissionDeniedError("Insufficient resume permissions", details=[{"code": "resume_access_denied"}])

    def _recruiter_has_candidate_application(self, current_user: User, resume: Resume) -> bool:
        recruiter_profile = self.recruiter_repository.get_by_user_id(current_user.id)
        if not recruiter_profile:
            return False
        applications = self.application_repository.list_by_candidate(resume.candidate_id)
        for application in applications:
            job = self.job_repository.get_by_id(application.job_id)
            if job and job.recruiter_id == recruiter_profile.id:
                return True
        return False

    @staticmethod
    def _extract_file_type(file_name: str) -> str:
        return Path(file_name).suffix.lower().lstrip(".")

    @staticmethod
    def _has_role(user: User, role_name: str) -> bool:
        return any(role.name == role_name for role in user.roles)
