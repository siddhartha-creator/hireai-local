from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.security import decode_access_token
from app.models.user import User
from app.modules.ai_services.matching.rule_based_engine import RuleBasedMatchingEngine
from app.modules.auth.service import AuthService
from app.modules.applications.repository import ApplicationRepository
from app.modules.applications.service import ApplicationService
from app.modules.candidates.repository import CandidateRepository
from app.modules.candidates.service import CandidateService
from app.modules.jobs.repository import JobRepository
from app.modules.jobs.service import JobService
from app.modules.recruiters.repository import RecruiterRepository
from app.modules.recruiters.service import RecruiterService
from app.modules.resumes.parser import ResumeParserService
from app.modules.resumes.repository import ResumeRepository
from app.modules.resumes.service import ResumeService
from app.modules.resumes.skills import SkillExtractionService
from app.modules.resumes.storage import ResumeStorageService
from app.modules.roles.repository import RoleRepository
from app.modules.scoring.repository import ScoringRepository
from app.modules.scoring.service import ScoringService
from app.modules.users.repository import UserRepository


DatabaseSession = Annotated[Session, Depends(get_db_session)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_auth_service(db: DatabaseSession) -> AuthService:
    return AuthService(UserRepository(db), RoleRepository(db))


def get_candidate_service(db: DatabaseSession) -> CandidateService:
    return CandidateService(CandidateRepository(db))


def get_recruiter_service(db: DatabaseSession) -> RecruiterService:
    return RecruiterService(RecruiterRepository(db))


def get_job_service(db: DatabaseSession) -> JobService:
    return JobService(JobRepository(db), RecruiterRepository(db))


def get_application_service(db: DatabaseSession) -> ApplicationService:
    return ApplicationService(
        ApplicationRepository(db),
        JobRepository(db),
        CandidateRepository(db),
        RecruiterRepository(db),
    )


def get_resume_service(db: DatabaseSession) -> ResumeService:
    return ResumeService(
        ResumeRepository(db),
        CandidateRepository(db),
        RecruiterRepository(db),
        JobRepository(db),
        ApplicationRepository(db),
        ResumeStorageService(),
        ResumeParserService(),
        SkillExtractionService(),
    )


def get_scoring_service(db: DatabaseSession) -> ScoringService:
    return ScoringService(
        ScoringRepository(db),
        ApplicationRepository(db),
        CandidateRepository(db),
        JobRepository(db),
        RecruiterRepository(db),
        ResumeRepository(db),
        RuleBasedMatchingEngine(),
    )


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise AuthenticationError("Invalid or expired access token", details=[{"code": "invalid_token"}]) from exc

    subject = payload.get("sub")
    if not subject:
        raise AuthenticationError("Invalid access token", details=[{"code": "missing_subject"}])

    return auth_service.get_current_user_by_id(str(subject))


CurrentUserDependency = Annotated[User, Depends(get_current_user)]


def require_roles(required_roles: list[str]):
    async def _dependency(current_user: CurrentUserDependency) -> User:
        user_roles = {role.name for role in current_user.roles}
        if not user_roles.intersection(required_roles):
            raise PermissionDeniedError(
                "Insufficient role permissions",
                details=[{"code": "insufficient_role", "required_roles": required_roles}],
            )
        return current_user

    return _dependency


def require_role(required_role: str):
    return require_roles([required_role])
