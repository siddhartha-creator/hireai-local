from uuid import UUID

from app.repositories.base import BaseRepository
from app.models.candidate import CandidateProfile


class CandidateRepository(BaseRepository[CandidateProfile]):
    """Candidate profile persistence."""

    def create_for_user(self, user_id: UUID) -> CandidateProfile:
        profile = CandidateProfile(user_id=user_id)
        self.db.add(profile)
        self.db.flush()
        self.db.refresh(profile)
        return profile

    def get_by_user_id(self, user_id: UUID) -> CandidateProfile | None:
        return self.db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()

    def get_by_id(self, candidate_id: UUID) -> CandidateProfile | None:
        return self.db.get(CandidateProfile, candidate_id)
