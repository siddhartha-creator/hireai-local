from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog
from app.models.application import Application
from app.models.interview import InterviewSession
from app.models.job import Job
from app.models.scoring import MatchScore
from app.models.user import User
from app.utils.seed_demo_data import seed_demo_data


def test_demo_seed_data_is_idempotent(db_session: Session) -> None:
    first = seed_demo_data(db_session)
    counts_after_first = {
        "users": db_session.query(User).count(),
        "jobs": db_session.query(Job).count(),
        "applications": db_session.query(Application).count(),
        "scores": db_session.query(MatchScore).count(),
        "interviews": db_session.query(InterviewSession).count(),
        "activity_logs": db_session.query(ActivityLog).count(),
    }

    second = seed_demo_data(db_session)
    counts_after_second = {
        "users": db_session.query(User).count(),
        "jobs": db_session.query(Job).count(),
        "applications": db_session.query(Application).count(),
        "scores": db_session.query(MatchScore).count(),
        "interviews": db_session.query(InterviewSession).count(),
        "activity_logs": db_session.query(ActivityLog).count(),
    }

    assert first == second
    assert counts_after_first == counts_after_second
    assert counts_after_first["users"] == 3
    assert counts_after_first["jobs"] == 3
    assert counts_after_first["applications"] == 2
    assert counts_after_first["scores"] == 1
    assert counts_after_first["interviews"] == 1
    assert counts_after_first["activity_logs"] >= 5
