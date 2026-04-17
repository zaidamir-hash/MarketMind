from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RiskIndicatorComputeRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_symbol_input(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip().upper()
            if not normalized:
                raise ValueError("symbol must not be blank.")
            return normalized
        return value


class RiskIndicatorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    risk_id: uuid.UUID
    asset_id: uuid.UUID
    symbol: str | None = None
    beta: Decimal | None
    volatility_30d: Decimal
    rsi_14: Decimal | None
    volume_ratio: Decimal
    price_vs_52w_high: Decimal
    price_vs_sma50: Decimal
    market_cap_cat: str | None
    volatility_label: str
    momentum_label: str
    volume_label: str
    risk_score: Decimal | None
    risk_label: str | None
    computed_at: datetime


class RiskIndicatorComputeResponse(BaseModel):
    status: str
    message: str
    symbol: str
    risk_indicator: RiskIndicatorRead


class RiskIndicatorBatchItem(BaseModel):
    symbol: str
    status: str
    message: str | None = None
    computed_at: datetime | None = None


class RiskIndicatorBatchResponse(BaseModel):
    status: str
    message: str
    details: list[RiskIndicatorBatchItem]
