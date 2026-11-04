from datetime import datetime, timezone
from pydantic import EmailStr, field_validator
from sqlmodel import SQLModel, Field

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    full_name: str
    first_name: str
    last_name: str
    second_last_name: str | None = None
    username: str = Field(unique=True, index=True)
    birth_date: str
    document_type: str
    document_number: str
    city: str
    phone: str
    faculty: str
    career: str | None = None
    bio: str | None = None

    @field_validator("email")
    @classmethod
    def validate_unal(cls, v: str) -> str:
        if not v.endswith("@unal.edu.co"):
            raise ValueError("Correo institucional UNAL requerido")
        return v.lower()

class UserCreate(UserBase):
    password: str = Field(min_length=8)
    accept_terms: bool
    accept_data_policy: bool
    accept_commercial: bool = False

class User(UserBase, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"