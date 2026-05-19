from app.repositories.base import BaseRepository
from app.models.application import Application


class ApplicationRepository(BaseRepository[Application]):
    """Application persistence."""

    def create(self, *, job_id, candidate_id, cover_letter: str | None) -> Application:
        application = Application(job_id=job_id, candidate_id=candidate_id, cover_letter=cover_letter)
        self.db.add(application)
        self.db.flush()
        self.db.refresh(application)
        return application

    def get_by_id(self, application_id) -> Application | None:
        return self.db.get(Application, application_id)

    def get_by_job_and_candidate(self, *, job_id, candidate_id) -> Application | None:
        return (
            self.db.query(Application)
            .filter(Application.job_id == job_id, Application.candidate_id == candidate_id)
            .first()
        )

    def list_all(self) -> list[Application]:
        return self.db.query(Application).order_by(Application.applied_at.desc()).all()

    def list_by_candidate(self, candidate_id) -> list[Application]:
        return (
            self.db.query(Application)
            .filter(Application.candidate_id == candidate_id)
            .order_by(Application.applied_at.desc())
            .all()
        )

    def list_by_job(self, job_id) -> list[Application]:
        return (
            self.db.query(Application)
            .filter(Application.job_id == job_id)
            .order_by(Application.applied_at.desc())
            .all()
        )
