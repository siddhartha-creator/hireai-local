from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import GUID, Base


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("job_id", "candidate_id", name="uq_applications_job_id_candidate_id"),)

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    job_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("jobs.id"), nullable=False)
    candidate_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("candidate_profiles.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="submitted", nullable=False)
    cover_letter: Mapped[str | None] = mapped_column(Text)
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    job: Mapped["Job"] = relationship(back_populates="applications")
    candidate: Mapped["CandidateProfile"] = relationship(back_populates="applications")
    match_score: Mapped["MatchScore | None"] = relationship(back_populates="application", uselist=False)
    interview_sessions: Mapped[list["InterviewSession"]] = relationship(back_populates="application")
