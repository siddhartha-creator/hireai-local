from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import GUID, JSONBType, Base


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    application_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("applications.id"), nullable=False)
    candidate_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("candidate_profiles.id"), nullable=False)
    job_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("jobs.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="in_progress", nullable=False)
    overall_score: Mapped[float | None] = mapped_column(Float)
    feedback_json: Mapped[dict | None] = mapped_column(JSONBType)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    application: Mapped["Application"] = relationship(back_populates="interview_sessions")
    questions: Mapped[list["InterviewQuestion"]] = relationship(
        back_populates="session",
        order_by="InterviewQuestion.order_index",
    )


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("interview_sessions.id"), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(80), nullable=False)
    skill_tag: Mapped[str | None] = mapped_column(String(120))
    expected_signals_json: Mapped[dict | None] = mapped_column(JSONBType)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    session: Mapped[InterviewSession] = relationship(back_populates="questions")
    answer: Mapped["CandidateAnswer | None"] = relationship(back_populates="question", uselist=False)


class CandidateAnswer(Base):
    __tablename__ = "candidate_answers"
    __table_args__ = (UniqueConstraint("question_id", name="uq_candidate_answers_question_id"),)

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    question_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("interview_questions.id"), nullable=False)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[float | None] = mapped_column(Float)
    feedback_json: Mapped[dict | None] = mapped_column(JSONBType)
    answered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    question: Mapped[InterviewQuestion] = relationship(back_populates="answer")
