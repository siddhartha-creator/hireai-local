from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db_session
from app.core.config import settings
from app.main import create_app
from app.models.candidate import CandidateProfile
from app.models.application import Application
from app.models.job import Job
from app.models.interview import CandidateAnswer, InterviewQuestion, InterviewSession
from app.models.recruiter import RecruiterProfile
from app.models.resume import Resume
from app.models.scoring import MatchScore
from app.models.user import Role, User, UserRole
from app.utils.seed_roles import seed_default_roles


@pytest.fixture()
def db_session(tmp_path) -> Generator[Session, None, None]:
    settings.RESUME_UPLOAD_DIR = str(tmp_path / "storage" / "resumes")
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    tables = [
        User.__table__,
        Role.__table__,
        UserRole.__table__,
        CandidateProfile.__table__,
        RecruiterProfile.__table__,
        Job.__table__,
        Application.__table__,
        Resume.__table__,
        MatchScore.__table__,
        InterviewSession.__table__,
        InterviewQuestion.__table__,
        CandidateAnswer.__table__,
    ]
    for table in tables:
        table.create(bind=engine, checkfirst=True)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        seed_default_roles(db)
        yield db
    finally:
        db.close()
        for table in reversed(tables):
            table.drop(bind=engine, checkfirst=True)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def override_get_db_session() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
