from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.user import Role


DEFAULT_ROLES = {
    "admin": "Platform administrator with full local system access.",
    "recruiter": "Recruiter user who can manage jobs and hiring workflows.",
    "candidate": "Candidate user who can manage their profile and applications.",
}


def seed_default_roles(db: Session) -> None:
    for name, description in DEFAULT_ROLES.items():
        existing_role = db.query(Role).filter(Role.name == name).first()
        if not existing_role:
            db.add(Role(name=name, description=description))
    db.commit()


def main() -> None:
    db = SessionLocal()
    try:
        seed_default_roles(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
