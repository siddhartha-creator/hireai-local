from app.repositories.base import BaseRepository
from app.models.resume import Resume


class ResumeRepository(BaseRepository[Resume]):
    """Resume persistence."""

    def create(
        self,
        *,
        candidate_id,
        file_name: str,
        original_file_name: str,
        file_path: str,
        file_type: str,
        file_size: int,
        extracted_text: str,
        parsed_data_json: dict,
        extracted_skills_json: list[str],
        is_primary: bool,
    ) -> Resume:
        resume = Resume(
            candidate_id=candidate_id,
            file_name=file_name,
            original_file_name=original_file_name,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            extracted_text=extracted_text,
            parsed_data_json=parsed_data_json,
            extracted_skills_json=extracted_skills_json,
            is_primary=is_primary,
        )
        self.db.add(resume)
        self.db.flush()
        self.db.refresh(resume)
        return resume

    def get_by_id(self, resume_id) -> Resume | None:
        return self.db.get(Resume, resume_id)

    def list_by_candidate(self, candidate_id) -> list[Resume]:
        return (
            self.db.query(Resume)
            .filter(Resume.candidate_id == candidate_id)
            .order_by(Resume.uploaded_at.desc())
            .all()
        )

    def get_primary_by_candidate(self, candidate_id) -> Resume | None:
        return (
            self.db.query(Resume)
            .filter(Resume.candidate_id == candidate_id, Resume.is_primary.is_(True))
            .first()
        )

    def has_any_for_candidate(self, candidate_id) -> bool:
        return self.db.query(Resume).filter(Resume.candidate_id == candidate_id).first() is not None

    def unset_primary_for_candidate(self, candidate_id) -> None:
        self.db.query(Resume).filter(Resume.candidate_id == candidate_id, Resume.is_primary.is_(True)).update(
            {"is_primary": False},
            synchronize_session="fetch",
        )

    def delete(self, resume: Resume) -> None:
        self.db.delete(resume)
