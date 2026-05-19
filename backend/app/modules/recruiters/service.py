from uuid import UUID

from app.core.exceptions import ResourceNotFoundError
from app.models.recruiter import RecruiterProfile
from app.models.user import User
from app.modules.recruiters.repository import RecruiterRepository
from app.schemas.profiles import RecruiterProfileUpdate
from app.services.base import BaseService


class RecruiterService(BaseService):
    """Recruiter profile orchestration."""

    def __init__(self, recruiter_repository: RecruiterRepository) -> None:
        self.recruiter_repository = recruiter_repository

    def ensure_profile_for_user(self, user_id: UUID) -> RecruiterProfile:
        profile = self.recruiter_repository.get_by_user_id(user_id)
        if profile:
            return profile
        profile = self.recruiter_repository.create_for_user(user_id)
        self.recruiter_repository.db.commit()
        self.recruiter_repository.db.refresh(profile)
        return profile

    def get_own_profile(self, current_user: User) -> RecruiterProfile:
        return self.ensure_profile_for_user(current_user.id)

    def update_own_profile(self, current_user: User, payload: RecruiterProfileUpdate) -> RecruiterProfile:
        profile = self.ensure_profile_for_user(current_user.id)
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None and key == "company_website":
                value = str(value)
            setattr(profile, key, value)
        profile.is_completed = self.is_profile_completed(profile)
        self.recruiter_repository.db.commit()
        self.recruiter_repository.db.refresh(profile)
        return profile

    def get_profile_by_id(self, recruiter_id: UUID) -> RecruiterProfile:
        profile = self.recruiter_repository.get_by_id(recruiter_id)
        if not profile:
            raise ResourceNotFoundError("Recruiter profile not found", details=[{"code": "recruiter_profile_not_found"}])
        return profile

    @staticmethod
    def is_profile_completed(profile: RecruiterProfile) -> bool:
        return all(
            [
                bool(profile.company_name),
                bool(profile.industry),
                bool(profile.position),
                bool(profile.location),
            ]
        )
