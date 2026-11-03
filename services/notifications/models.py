from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class Notification(SQLModel, table=True):
    __tablename__ = "notifications"
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    type: str
    message: str
    related_id: int | None = Field(default=None)
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))