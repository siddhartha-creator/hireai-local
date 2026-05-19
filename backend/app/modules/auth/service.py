from uuid import UUID

from app.core.exceptions import AuthenticationError, ConflictError, PermissionDeniedError, ResourceNotFoundError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.modules.candidates.repository import CandidateRepository
from app.modules.recruiters.repository import RecruiterRepository
from app.modules.roles.repository import RoleRepository
from app.modules.users.repository import UserRepository
from app.schemas.auth import TokenResponse, UserCreate, UserLogin
from app.services.base import BaseService


class AuthService(BaseService):
    def __init__(self, user_repository: UserRepository, role_repository: RoleRepository) -> None:
        self.user_repository = user_repository
        self.role_repository = role_repository

    def register(self, payload: UserCreate) -> User:
        existing_user = self.user_repository.get_by_email(payload.email)
        if existing_user:
            raise ConflictError("Email is already registered", details=[{"field": "email", "code": "email_exists"}])

        role = self.role_repository.get_by_name(payload.role)
        if not role:
            raise ResourceNotFoundError("Requested role does not exist", details=[{"field": "role", "code": "role_not_found"}])

        user = self.user_repository.create(
            email=str(payload.email),
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
        )
        self.role_repository.assign_role(user, role)
        if payload.role == "candidate":
            CandidateRepository(self.user_repository.db).create_for_user(user.id)
        elif payload.role == "recruiter":
            RecruiterRepository(self.user_repository.db).create_for_user(user.id)
        self.user_repository.db.commit()
        self.user_repository.db.refresh(user)
        return user

    def login(self, payload: UserLogin) -> TokenResponse:
        user = self.user_repository.get_by_email(str(payload.email))
        if not user or not verify_password(payload.password, user.hashed_password):
            raise AuthenticationError("Invalid email or password", details=[{"code": "invalid_credentials"}])
        if not user.is_active:
            raise PermissionDeniedError("User account is inactive", details=[{"code": "inactive_user"}])

        roles = self._role_names(user)
        token = create_access_token(
            subject=str(user.id),
            claims={
                "email": user.email,
                "roles": roles,
            },
        )
        return TokenResponse(access_token=token, user=user)

    def get_current_user_by_id(self, user_id: str) -> User:
        try:
            parsed_user_id = UUID(user_id)
        except ValueError as exc:
            raise AuthenticationError("Invalid access token subject", details=[{"code": "invalid_subject"}]) from exc
        user = self.user_repository.get_by_id(parsed_user_id)
        if not user:
            raise AuthenticationError("Authenticated user no longer exists", details=[{"code": "user_not_found"}])
        if not user.is_active:
            raise PermissionDeniedError("User account is inactive", details=[{"code": "inactive_user"}])
        return user

    @staticmethod
    def _role_names(user: User) -> list[str]:
        return [role.name for role in user.roles]
