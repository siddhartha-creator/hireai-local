from app.models.user import Role, User
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def get_by_name(self, name: str) -> Role | None:
        return self.db.query(Role).filter(Role.name == name).first()

    def list_by_names(self, names: list[str]) -> list[Role]:
        return self.db.query(Role).filter(Role.name.in_(names)).all()

    def assign_role(self, user: User, role: Role) -> User:
        if role not in user.roles:
            user.roles.append(role)
            self.db.flush()
            self.db.refresh(user)
        return user
