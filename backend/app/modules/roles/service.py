from app.models.user import Role
from app.modules.roles.repository import RoleRepository
from app.services.base import BaseService


class RoleService(BaseService):
    def __init__(self, role_repository: RoleRepository) -> None:
        self.role_repository = role_repository

    def get_required_role(self, name: str) -> Role | None:
        return self.role_repository.get_by_name(name)
