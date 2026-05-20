from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import GUID, JSONBType, Base
from app.core.time import utc_now


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    recruiter_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("recruiter_profiles.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements_json: Mapped[list | dict | None] = mapped_column(JSONBType)
    skills_json: Mapped[list | dict | None] = mapped_column(JSONBType)
    seniority: Mapped[str | None] = mapped_column(String(100))
    location: Mapped[str | None] = mapped_column(String(255))
    employment_type: Mapped[str | None] = mapped_column(String(50))
    salary_min: Mapped[float | None] = mapped_column(Float)
    salary_max: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    recruiter: Mapped["RecruiterProfile"] = relationship(back_populates="jobs")
    applications: Mapped[list["Application"]] = relationship(back_populates="job")
    match_scores: Mapped[list["MatchScore"]] = relationship(back_populates="job")
