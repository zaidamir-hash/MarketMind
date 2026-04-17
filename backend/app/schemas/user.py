from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    username: str
    email: str
    full_name: str | None
    created_at: datetime
    is_active: bool


class CurrentUserRead(UserRead):
    pass
