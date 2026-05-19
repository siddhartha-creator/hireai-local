from app.repositories.base import BaseRepository
from app.models.job import Job


class JobRepository(BaseRepository[Job]):
    """Job persistence."""

    def create(self, *, recruiter_id, payload) -> Job:
        job = Job(recruiter_id=recruiter_id, **payload.model_dump(exclude={"recruiter_id"}))
        self.db.add(job)
        self.db.flush()
        self.db.refresh(job)
        return job

    def get_by_id(self, job_id) -> Job | None:
        return self.db.get(Job, job_id)

    def list_all(self) -> list[Job]:
        return self.db.query(Job).order_by(Job.created_at.desc()).all()

    def list_open(self) -> list[Job]:
        return self.db.query(Job).filter(Job.status == "open").order_by(Job.created_at.desc()).all()

    def list_by_recruiter(self, recruiter_id) -> list[Job]:
        return self.db.query(Job).filter(Job.recruiter_id == recruiter_id).order_by(Job.created_at.desc()).all()
