from app.services.base import BaseService


class ActivityLogService(BaseService):
    """Audit trail service placeholder.

    Phase 2+ services will call this boundary after important domain events.
    """

    def record(self, action: str, *, actor_user_id: str | None = None, metadata: dict | None = None) -> None:
        return None
