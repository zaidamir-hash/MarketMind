from __future__ import annotations

from datetime import timedelta

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.models import User
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserRead


def register_user(db: Session, request: RegisterRequest) -> User:
    existing_username = db.scalar(
        select(User).where(User.username == request.username)
    )
    if existing_username is not None:
        raise ValueError("Username already exists.")

    existing_email = db.scalar(
        select(User).where(User.email == request.email)
    )
    if existing_email is not None:
        raise ValueError("Email already exists.")

    user = User(
        username=request.username,
        email=request.email,
        password_hash=get_password_hash(request.password),
        full_name=request.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username_or_email: str, password: str) -> User | None:
    user = db.scalar(
        select(User).where(
            or_(User.username == username_or_email, User.email == username_or_email)
        )
    )
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user


def build_token_response(user: User) -> TokenResponse:
    settings = get_settings()
    access_token = create_access_token(
        subject=str(user.user_id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserRead.model_validate(user),
    )
