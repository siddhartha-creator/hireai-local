from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import GUID, JSONBType, Base
from app.core.time import utc_now


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    actor_user_id: Mapped[UUID | None] = mapped_column(GUID(), ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(120))
    entity_id: Mapped[UUID | None] = mapped_column(GUID())
    metadata_json: Mapped[dict | None] = mapped_column(JSONBType)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
