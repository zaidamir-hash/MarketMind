from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.asset import normalize_symbol


class AlertCreate(BaseModel):
    symbol: str | None = Field(default=None, max_length=20)
    asset_id: uuid.UUID | None = None
    condition: str = Field(min_length=5, max_length=10)
    threshold: Decimal

    @model_validator(mode="after")
    def validate_asset_reference(self) -> "AlertCreate":
        if not self.symbol and not self.asset_id:
            raise ValueError("Provide either symbol or asset_id.")
        if self.symbol:
            self.symbol = normalize_symbol(self.symbol)
        self.condition = self.condition.strip().upper()
        if self.condition not in {"ABOVE", "BELOW"}:
            raise ValueError("condition must be ABOVE or BELOW.")
        if self.threshold < 0:
            raise ValueError("threshold must be non-negative.")
        return self


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    alert_id: uuid.UUID
    user_id: uuid.UUID
    asset_id: uuid.UUID
    symbol: str | None = None
    condition: str
    threshold: Decimal
    is_active: bool
    created_at: datetime


class AlertLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    log_id: uuid.UUID
    alert_id: uuid.UUID
    symbol: str | None = None
    triggered_price: Decimal
    fired_at: datetime
