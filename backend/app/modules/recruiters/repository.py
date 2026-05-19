from uuid import UUID

from app.repositories.base import BaseRepository
from app.models.recruiter import RecruiterProfile


class RecruiterRepository(BaseRepository[RecruiterProfile]):
    """Recruiter profile persistence."""

    def create_for_user(self, user_id: UUID) -> RecruiterProfile:
        profile = RecruiterProfile(user_id=user_id)
        self.db.add(profile)
        self.db.flush()
        self.db.refresh(profile)
        return profile

    def get_by_user_id(self, user_id: UUID) -> RecruiterProfile | None:
        return self.db.query(RecruiterProfile).filter(RecruiterProfile.user_id == user_id).first()

    def get_by_id(self, recruiter_id: UUID) -> RecruiterProfile | None:
        return self.db.get(RecruiterProfile, recruiter_id)
