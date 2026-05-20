from app.repositories.base import BaseRepository
from app.models.activity_log import ActivityLog


class ActivityLogRepository(BaseRepository[ActivityLog]):
    """Activity log persistence."""

    def create(
        self,
        *,
        action: str,
        actor_user_id=None,
        entity_type: str | None = None,
        entity_id=None,
        metadata_json: dict | None = None,
    ) -> ActivityLog:
        log = ActivityLog(
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=metadata_json,
        )
        self.db.add(log)
        self.db.flush()
        self.db.refresh(log)
        return log
