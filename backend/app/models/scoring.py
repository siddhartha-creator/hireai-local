from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import GUID, JSONBType, Base
from app.core.time import utc_now


class MatchScore(Base):
    __tablename__ = "match_scores"
    __table_args__ = (UniqueConstraint("application_id", name="uq_match_scores_application_id"),)

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    application_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("applications.id"), nullable=False)
    candidate_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("candidate_profiles.id"), nullable=False)
    job_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("jobs.id"), nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    skill_score: Mapped[float] = mapped_column(Float, nullable=False)
    experience_score: Mapped[float] = mapped_column(Float, nullable=False)
    education_score: Mapped[float] = mapped_column(Float, nullable=False)
    location_score: Mapped[float] = mapped_column(Float, nullable=False)
    explanation_json: Mapped[dict] = mapped_column(JSONBType, nullable=False)
    matched_skills_json: Mapped[list] = mapped_column(JSONBType, nullable=False)
    missing_skills_json: Mapped[list] = mapped_column(JSONBType, nullable=False)
    scoring_version: Mapped[str] = mapped_column(String(80), default="rule_based_v1", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    application: Mapped["Application"] = relationship(back_populates="match_score")
    candidate: Mapped["CandidateProfile"] = relationship(back_populates="match_scores")
    job: Mapped["Job"] = relationship(back_populates="match_scores")
