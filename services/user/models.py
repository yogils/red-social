from datetime import datetime, timezone
from pydantic import BaseModel
from sqlmodel import SQLModel, Field

class UserProfile(SQLModel, table=True):
    __tablename__ = "user_profiles"
    id: int = Field(primary_key=True)
    full_name: str
    career: str | None = None
    bio: str | None = None 
    profile_picture_url: str | None = None
    cover_picture_url: str | None = None
    faculty: str | None = None

class Post(SQLModel, table=True):
    __tablename__ = "posts"
    id: int | None = Field(default=None, primary_key=True)
    author_id: int = Field(index=True)
    author_name: str
    content: str
    image_url: str | None = None
    reports: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Reaction(SQLModel, table=True):
    __tablename__ = "reactions"
    id: int | None = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="posts.id", index=True)
    user_id: int = Field(index=True)
    reaction_type: str

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    id: int | None = Field(default=None, primary_key=True)
    sender_id: int = Field(index=True)
    receiver_id: int = Field(index=True)
    content: str | None = None
    file_url: str | None = None
    file_type: str | None = None
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Comment(SQLModel, table=True):
    __tablename__ = "comments"
    id: int | None = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="posts.id", index=True)
    author_id: int = Field(index=True)
    author_name: str
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PostCreate(BaseModel):
    author_id: int
    author_name: str
    content: str
    image_url: str | None = None

class MessageCreate(BaseModel):
    sender_id: int
    receiver_id: int
    content: str | None = None
    file_url: str | None = None
    file_type: str | None = None

class ReactionCreate(BaseModel):
    reaction_type: str

class UserProfileCreate(BaseModel):
    id: int
    full_name: str
    career: str | None = None
    bio: str | None = None
    cover_picture_url: str | None = None
    faculty: str | None = None

class CommentCreate(BaseModel):
    author_id: int
    author_name: str
    content: str