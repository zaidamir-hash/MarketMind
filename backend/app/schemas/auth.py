from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.user import UserRead


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=8, max_length=255)
    full_name: str | None = Field(default=None, max_length=100)

    @field_validator("username", "email", "password", mode="before")
    @classmethod
    def strip_required_strings(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("full_name", mode="before")
    @classmethod
    def strip_optional_string(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value


class LoginRequest(BaseModel):
    username_or_email: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=1, max_length=255)

    @field_validator("username_or_email", "password", mode="before")
    @classmethod
    def strip_values(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class TokenPayload(BaseModel):
    sub: str


class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: str = "bearer"
    user: UserRead
