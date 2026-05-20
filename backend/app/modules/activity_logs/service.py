from app.services.base import BaseService
from app.modules.activity_logs.repository import ActivityLogRepository


class ActivityLogService(BaseService):
    """Audit trail service.

    Logging should never break the primary user workflow, so callers can use
    this as a best-effort boundary.
    """

    def __init__(self, repository: ActivityLogRepository) -> None:
        self.repository = repository

    def record(
        self,
        action: str,
        *,
        actor_user_id=None,
        entity_type: str | None = None,
        entity_id=None,
        metadata: dict | None = None,
        commit: bool = True,
    ) -> None:
        try:
            self.repository.create(
                action=action,
                actor_user_id=actor_user_id,
                entity_type=entity_type,
                entity_id=entity_id,
                metadata_json=metadata,
            )
            if commit:
                self.repository.db.commit()
        except Exception:
            self.repository.db.rollback()
