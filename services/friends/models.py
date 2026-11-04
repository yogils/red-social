from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class AuthUser(SQLModel, table=True):
    __tablename__ = "users"
    id: int = Field(primary_key=True)
    email: str
    full_name: str
    faculty: str | None = None

class Friendship(SQLModel, table=True):
    __tablename__ = "friendships"
    id: int | None = Field(default=None, primary_key=True)
    user_id_1: int = Field(index=True)
    user_id_2: int = Field(index=True)
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))