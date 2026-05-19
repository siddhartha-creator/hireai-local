from uuid import UUID

from app.core.exceptions import ResourceNotFoundError
from app.models.candidate import CandidateProfile
from app.models.user import User
from app.modules.candidates.repository import CandidateRepository
from app.schemas.profiles import CandidateProfileUpdate
from app.services.base import BaseService


class CandidateService(BaseService):
    """Candidate profile orchestration."""

    def __init__(self, candidate_repository: CandidateRepository) -> None:
        self.candidate_repository = candidate_repository

    def ensure_profile_for_user(self, user_id: UUID) -> CandidateProfile:
        profile = self.candidate_repository.get_by_user_id(user_id)
        if profile:
            return profile
        profile = self.candidate_repository.create_for_user(user_id)
        self.candidate_repository.db.commit()
        self.candidate_repository.db.refresh(profile)
        return profile

    def get_own_profile(self, current_user: User) -> CandidateProfile:
        return self.ensure_profile_for_user(current_user.id)

    def update_own_profile(self, current_user: User, payload: CandidateProfileUpdate) -> CandidateProfile:
        profile = self.ensure_profile_for_user(current_user.id)
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None and key.endswith("_url"):
                value = str(value)
            setattr(profile, key, value)
        profile.is_completed = self.is_profile_completed(profile)
        self.candidate_repository.db.commit()
        self.candidate_repository.db.refresh(profile)
        return profile

    def get_profile_by_id(self, candidate_id: UUID) -> CandidateProfile:
        profile = self.candidate_repository.get_by_id(candidate_id)
        if not profile:
            raise ResourceNotFoundError("Candidate profile not found", details=[{"code": "candidate_profile_not_found"}])
        return profile

    @staticmethod
    def is_profile_completed(profile: CandidateProfile) -> bool:
        skills = profile.skills_json or []
        has_skills = len(skills) > 0 if isinstance(skills, (list, dict)) else False
        return all(
            [
                bool(profile.headline),
                bool(profile.summary),
                has_skills,
                profile.experience_years is not None,
                bool(profile.location),
            ]
        )
